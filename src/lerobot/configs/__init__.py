# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
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

"""
Public API for lerobot configuration types and base config classes.

NOTE: TrainPipelineConfig, EvalPipelineConfig, and TrainRLServerPipelineConfig
are intentionally NOT re-exported here to avoid circular dependencies
(they import lerobot.envs and lerobot.policies at module level).
Import them directly: ``from lerobot.configs.train import TrainPipelineConfig``
"""

from importlib import import_module

__all__ = [
    # Types
    "FeatureType",
    "NormalizationMode",
    "PipelineFeatureType",
    "PolicyFeature",
    "RTCAttentionSchedule",
    # Config classes
    "DatasetRecordConfig",
    "DatasetConfig",
    "EvalConfig",
    "PeftConfig",
    "PreTrainedConfig",
    "WandBConfig",
    "VideoEncoderConfig",
    "DepthEncoderConfig",
    # Defaults
    "camera_encoder_defaults",
    "depth_encoder_defaults",
    # Constants
    "VALID_VIDEO_CODECS",
    "VIDEO_ENCODER_INFO_KEYS",
]

_LAZY_EXPORTS = {
    "DatasetRecordConfig": ".dataset",
    "DatasetConfig": ".default",
    "EvalConfig": ".default",
    "PeftConfig": ".default",
    "WandBConfig": ".default",
    "PreTrainedConfig": ".policies",
    "FeatureType": ".types",
    "NormalizationMode": ".types",
    "PipelineFeatureType": ".types",
    "PolicyFeature": ".types",
    "RTCAttentionSchedule": ".types",
    "VALID_VIDEO_CODECS": ".video",
    "VIDEO_ENCODER_INFO_KEYS": ".video",
    "DepthEncoderConfig": ".video",
    "VideoEncoderConfig": ".video",
    "camera_encoder_defaults": ".video",
    "depth_encoder_defaults": ".video",
}


def __getattr__(name: str) -> object:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_LAZY_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
