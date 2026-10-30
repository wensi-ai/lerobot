"""Regression tests for B1K metadata, read imports, and encoder backpressure."""

import queue
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from lerobot.configs import DepthEncoderConfig, RGBEncoderConfig
from lerobot.datasets import LeRobotDataset
from lerobot.datasets.io_utils import write_info
from lerobot.datasets.utils import DatasetInfo
from lerobot.datasets.video_utils import StreamingVideoEncoder

pytestmark = pytest.mark.dataset


def test_b1k_streaming_depth_resume_and_read(tmp_path):
    root = tmp_path / "b1k"
    key = "observation.depth_linear.head"
    kwargs = {
        "repo_id": "test/b1k",
        "root": root,
        "streaming_encoding": True,
        "encoder_queue_maxsize": 1,
        "encoder_threads": 1,
        "rgb_encoder": RGBEncoderConfig(vcodec="hevc", g=8, crf=30),
        "depth_encoder": DepthEncoderConfig(
            g=8, crf=0, extra_options={"x265-params": "log-level=0:bframes=0"}
        ),
    }
    dataset = LeRobotDataset.create(
        fps=30,
        features={
            "observation.rgb.head": {"dtype": "video", "shape": (64, 64, 3), "names": None},
            key: {
                "dtype": "video",
                "shape": (64, 64, 1),
                "names": None,
                "info": {"is_depth_map": True, "depth_unit": "m"},
            },
        },
        **kwargs,
    )
    dataset.meta.info.cam_intrinsics = {"head": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]}
    dataset.meta.info.omnigibson_git_hash = "test-revision"
    write_info(dataset.meta.info, root)

    for count in [4, 1]:
        for _ in range(count):
            dataset.add_frame(
                {
                    "observation.rgb.head": np.zeros((64, 64, 3), dtype=np.uint8),
                    key: np.full((64, 64, 1), 2.0, dtype=np.float32),
                    "task": "test task",
                }
            )
        dataset.save_episode()
        dataset.finalize()
        if count == 4:
            dataset = LeRobotDataset.resume(**kwargs)

    reader = LeRobotDataset("test/b1k", root=root, video_backend="pyav", depth_output_unit="m")
    assert len(reader) == 5
    assert reader.meta.total_episodes == 2
    assert reader.meta.info.omnigibson_git_hash == "test-revision"
    assert "head" in reader.meta.info.cam_intrinsics
    assert reader.meta.features[key]["info"]["depth_unit"] == "m"
    for index in range(len(reader)):
        np.testing.assert_allclose(reader[index][key].numpy(), 2.0, atol=0.003)


def test_read_import_does_not_load_torchvision():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from lerobot.datasets import LeRobotDataset; "
            "from lerobot.configs import DepthEncoderConfig, RGBEncoderConfig; "
            "assert 'torchvision' not in sys.modules; "
            "assert 'lerobot.datasets.dataset_writer' not in sys.modules",
        ],
        check=True,
    )


def test_b1k_metadata_roundtrip():
    info = DatasetInfo(codebase_version="v3.0", fps=30, features={})
    info.cam_intrinsics = {"head": [[100.0, 0.0, 32.0], [0.0, 100.0, 32.0], [0.0, 0.0, 1.0]]}
    info.omnigibson_git_hash = "test-revision"
    restored = DatasetInfo.from_dict(info.to_dict())
    assert restored.cam_intrinsics == info.cam_intrinsics
    assert restored.omnigibson_git_hash == info.omnigibson_git_hash


def test_full_queue_retries_the_same_frame():
    frame_queue = Mock()
    frame_queue.put.side_effect = [queue.Full, None]
    encoder = StreamingVideoEncoder(fps=30)
    encoder._episode_active = True
    encoder._threads = {"cam": SimpleNamespace(is_alive=lambda: True)}
    encoder._frame_queues = {"cam": frame_queue}
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    try:
        encoder.feed_frame("cam", image)
        assert frame_queue.put.call_count == 2
        queued = frame_queue.put.call_args_list[0].args[0]
        assert queued is not image
        assert frame_queue.put.call_args_list[1].args[0] is queued
    finally:
        encoder._episode_active = False
        encoder._threads = {}
        encoder._frame_queues = {}
        encoder.close()


def test_encoder_crash_while_queue_is_full():
    frame_queue = Mock()
    frame_queue.put.side_effect = queue.Full
    alive = Mock(side_effect=[True, False])
    result_queue = queue.Queue()
    result_queue.put(("error", "test failure"))
    encoder = StreamingVideoEncoder(fps=30)
    encoder._episode_active = True
    encoder._threads = {"cam": SimpleNamespace(is_alive=alive)}
    encoder._frame_queues = {"cam": frame_queue}
    encoder._result_queues = {"cam": result_queue}
    try:
        with pytest.raises(RuntimeError, match="test failure"):
            encoder.feed_frame("cam", np.zeros((16, 16, 3), dtype=np.uint8))
    finally:
        encoder._episode_active = False
        encoder._threads = {}
        encoder._frame_queues = {}
        encoder.close()
