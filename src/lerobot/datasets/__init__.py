#!/usr/bin/env python

# Copyright 2026 The HuggingFace Inc. team.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lerobot.utils.import_utils import require_package

require_package("datasets", extra="dataset")
require_package("av", extra="dataset")

# NOTE: Low-level I/O functions (cast_stats_to_numpy, get_parquet_file_size_in_mb, etc.)
# and legacy migration constants are intentionally NOT re-exported here.
# Import directly: ``from lerobot.datasets.io_utils import ...``

__all__ = [
    "CODEBASE_VERSION",
    "DEFAULT_EPISODES_PATH",
    "DEFAULT_QUANTILES",
    "EpisodeAwareSampler",
    "LeRobotDataset",
    "LeRobotDatasetMetadata",
    "MultiLeRobotDataset",
    "StreamingLeRobotDataset",
    "VideoEncodingManager",
    "check_video_encoder_parameters_pyav",
    "detect_available_encoders_pyav",
    "add_features",
    "aggregate_datasets",
    "aggregate_pipeline_dataset_features",
    "aggregate_stats",
    "convert_image_to_video_dataset",
    "create_initial_features",
    "create_lerobot_dataset_card",
    "delete_episodes",
    "get_feature_stats",
    "load_episodes",
    "make_dataset",
    "merge_datasets",
    "modify_features",
    "modify_tasks",
    "recompute_stats",
    "remove_feature",
    "resolve_delta_timestamps",
    "safe_stop_image_writer",
    "split_dataset",
    "write_stats",
]

_LAZY_EXPORTS = {
    "CODEBASE_VERSION": ".dataset_metadata",
    "DEFAULT_EPISODES_PATH": ".utils",
    "DEFAULT_QUANTILES": ".compute_stats",
    "EpisodeAwareSampler": ".sampler",
    "LeRobotDataset": ".lerobot_dataset",
    "LeRobotDatasetMetadata": ".dataset_metadata",
    "MultiLeRobotDataset": ".multi_dataset",
    "StreamingLeRobotDataset": ".streaming_dataset",
    "VideoEncodingManager": ".video_utils",
    "check_video_encoder_parameters_pyav": ".pyav_utils",
    "detect_available_encoders_pyav": ".pyav_utils",
    "add_features": ".dataset_tools",
    "aggregate_datasets": ".aggregate",
    "aggregate_pipeline_dataset_features": ".pipeline_features",
    "aggregate_stats": ".compute_stats",
    "convert_image_to_video_dataset": ".dataset_tools",
    "create_initial_features": ".pipeline_features",
    "create_lerobot_dataset_card": ".utils",
    "delete_episodes": ".dataset_tools",
    "get_feature_stats": ".compute_stats",
    "load_episodes": ".io_utils",
    "make_dataset": ".factory",
    "merge_datasets": ".dataset_tools",
    "modify_features": ".dataset_tools",
    "modify_tasks": ".dataset_tools",
    "recompute_stats": ".dataset_tools",
    "remove_feature": ".dataset_tools",
    "resolve_delta_timestamps": ".factory",
    "safe_stop_image_writer": ".image_writer",
    "split_dataset": ".dataset_tools",
    "write_stats": ".io_utils",
}


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
