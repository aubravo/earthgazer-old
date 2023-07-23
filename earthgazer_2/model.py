import pathlib
import tensorflow as tf

data_dir = pathlib.Path('D:\\dataset_rgb\\').with_suffix('')

train_ds = tf.keras.utils.image_dataset_from_directory(data_dir,
                                                       subset="training",
                                                       validation_split=0.8,
                                                       seed=123)
val_ds = tf.keras.utils.image_dataset_from_directory(data_dir,
                                                        subset="validation",
                                                        validation_split=0.2,
                                                        seed=123)

class_names = train_ds.class_names
print(class_names)
