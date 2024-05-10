from enum import Enum


class ImageFormat(Enum):
    TIFF = "tiff"
    JPEG = "jpeg"
    JPEG2000 = "jpeg2000"
    PNG = "png"


class StorageType(Enum):
    LOCAL = "local"
    REMOTE = "remote"


TransformationType = Enum(
    value="TransformationType",
    names=[
        ("ONE_TO_ONE", "one_to_one"),
        ("one_to_one", "one_to_one"),
        ("1-1", "one_to_one"),
        ("ONE_TO_MANY", "one_to_many"),
        ("one_to_many", "one_to_many"),
        ("1-n", "one_to_many"),
        ("MANY_TO_ONE", "many_to_one"),
        ("many_to_one", "many_to_one"),
        ("n-n", "many_to_many"),
    ]
)
