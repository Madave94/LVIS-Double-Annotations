import json
import os
from collections import defaultdict
from copy import deepcopy
import random

def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

def update_to_lvis_final(data, old_to_new_id_mapping, new_categories, rater_id):
    # Rename image key "not_exhaustive" in v0.5 with key "not_exhaustive_category_ids" in v1.0
    for image in data["images"]:
        image["not_exhaustive_category_ids"] = image.pop("not_exhaustive")
    # Filter annotations to include only those with correct categories
    # Also add a generic rater ID
    count = defaultdict(list)
    new_annotations = []
    for annotation in data["annotations"]:
        if annotation["category_id"] in old_to_new_id_mapping.keys():
            annotation["category_id"] = old_to_new_id_mapping[annotation["category_id"]]
            annotation["rater_id"] = rater_id
            new_annotations.append(annotation)
            count[annotation["category_id"]].append(annotation["image_id"])
    data["annotations"] = new_annotations
    instance_count = {}
    image_count = {}
    for key, value in count.items():
        instance_count[key] = len(value)
        image_count[key] = len(set(value))
    data["categories"] = deepcopy(new_categories)
    # Add instance count, frequency, image count
    for cat in data["categories"]:
        cat_id = cat["id"]
        ic_current = instance_count.get(cat_id, 0)
        cat["instance_count"] = ic_current
        cat["image_count"] = image_count.get(cat_id, 0)
        # Frequency assignment
        if ic_current <= 10:
            cat["frequency"] = "r"
        elif ic_current < 100:
            cat["frequency"] = "c"
        else:
            cat["frequency"] = "f"
    return data

if __name__ == "__main__":
    # Define the original and new directories
    original_dir = "original_double_annos_v0.5"
    processed_dir = "processed_double_annos_v1.0"

    # Paths to the original annotation files
    lvis_r1_path = os.path.join(original_dir, "lvis_v0.5_val_r1.json")
    lvis_r2_path = os.path.join(original_dir, "lvis_v0.5_val_r2.json")

    # Load the original annotations
    lvis_r1 = load_json(lvis_r1_path)
    lvis_r2 = load_json(lvis_r2_path)

    # Path to the LVIS v1.0 original annotations
    lvis_original_path = "original_annos_v1.0/lvis_v1.0_val.json"
    lvis_original = load_json(lvis_original_path)

    # Map category names to IDs
    name_to_cat_v1_0 = {cat["synset"]: cat["id"] for cat in lvis_original["categories"]}
    name_to_cat_v0_5 = {cat["synset"]: cat["id"] for cat in lvis_r1["categories"]}
    # Manually add stop_sign class
    # This class has no single instance in the lvis_consistency dataset but should still be part of the classes
    name_to_cat_v0_5["stop_sign.n.01"] = 1800  # Assign a placeholder ID
    old_to_new_id_category_mapping = {
        name_to_cat_v0_5[name]: name_to_cat_v1_0[name]
        for name in name_to_cat_v1_0.keys()
        if name in name_to_cat_v0_5
    }

    # Update the annotations to align with LVIS v1.0
    lvis_r1_updated = update_to_lvis_final(lvis_r1, old_to_new_id_category_mapping, lvis_original["categories"], "r1")
    lvis_r2_updated = update_to_lvis_final(lvis_r2, old_to_new_id_category_mapping, lvis_original["categories"], "r2")

    # merge image and instance from r1 and r2
    # 1) find the mapping from file_name to image_id
    # also add the rater_list to images
    file_name_to_image_id = {}
    for image in lvis_r1_updated["images"]:
        image["rater_list"] = ["r1", "r2"]
        file_name_to_image_id[image["file_name"]] = image["id"]

    # 2) find the mapping from r1 image ids to r2 image ids
    r2_id_to_r1_id =  {}
    for image in lvis_r2_updated["images"]:
        r2_id_to_r1_id[image["id"]] = file_name_to_image_id[image["file_name"]]

    # 3) check the annotation id number, to start counting where r1 does not use the annotation ids anymore
    # this is to prevent that any annotation id is used twice
    id_counter = max([annotation["id"] for annotation in lvis_r1_updated["annotations"]]) + 1

    # overwrite the image_ids and annotation ids
    annotations = lvis_r1_updated["annotations"]
    for annotation in lvis_r2_updated["annotations"]:
        annotation["image_id"] = r2_id_to_r1_id[annotation["image_id"]]
        annotation["id"] = id_counter
        id_counter += 1
        annotations.append(annotation)

    # create the dataset
    lvis_v1_full = {
        "info": lvis_original["info"],
        "annotations": annotations,
        "images": lvis_r1_updated["images"],
        "categories": lvis_r1_updated["categories"],
        "licenses": lvis_r1_updated["licenses"]
    }

    with open(processed_dir + "/" + "lvis_v1.0_val_doubly_annos.json", "w") as f:
        json.dump(lvis_v1_full, f)

    # ---------------------
    # Create a small subset
    # Set the number of images you want in the subset
    subset_size = 200

    # Ensure that the number of images is not more than the available images
    total_images = len(lvis_v1_full["images"])
    if subset_size > total_images:
        subset_size = total_images
        print(f"Requested subset size is larger than the total images. Using subset_size = {total_images}")

    # Randomly select 200 images
    subset_images = random.sample(lvis_v1_full["images"], subset_size)

    # Create a set of image IDs for faster lookup
    subset_image_ids = set(image["id"] for image in subset_images)

    # Filter annotations to include only those in the subset
    subset_annotations = [anno for anno in lvis_v1_full["annotations"] if anno["image_id"] in subset_image_ids]

    # Create the subset dataset
    lvis_v1_subset = {
        "info": lvis_v1_full["info"],
        "annotations": subset_annotations,
        "images": subset_images,
        "categories": lvis_v1_full["categories"],
        "licenses": lvis_v1_full["licenses"]
    }

    # Save the subset dataset
    subset_filename = "lvis_v1.0_val_doubly_annos_subset200.json"
    subset_output_path = os.path.join(processed_dir, subset_filename)
    with open(subset_output_path, "w") as f:
        json.dump(lvis_v1_subset, f)

    print(f"Subset dataset with {subset_size} images saved to {subset_output_path}")








