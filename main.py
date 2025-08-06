import os
import json
import re
import shutil

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a filename.
    Removes special characters and replaces spaces with nothing.
    """
    name = name.strip()
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', '', name)
    return name

def process_products():
    """
    Moves and renames product images and extracts product names.
    """
    # Load product data from JSON files
    try:
        with open('1.json', 'r') as f:
            data1 = json.load(f)
        with open('2.json', 'r') as f:
            data2 = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure 1.json and 2.json are in the same directory.")
        return

    all_products = data1['data']['products'] + data2['data']['products']
    product_map = {p['id']: p['name']['default'] for p in all_products}

    # Extract names to text files
    with open('1.txt', 'w') as f:
        for product in data1['data']['products']:
            f.write(product['name']['default'] + '\n')

    with open('2.txt', 'w') as f:
        for product in data2['data']['products']:
            f.write(product['name']['default'] + '\n')

    # Process images
    product_dir = 'product'
    if not os.path.isdir(product_dir):
        print(f"Directory '{product_dir}' not found.")
        return

    # Keep track of renamed files to append numbers if needed
    renamed_counts = {}

    for root, dirs, files in os.walk(product_dir):
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                path_parts = root.replace('\\', '/').split('/')

                # The product ID should be the directory right after 'product'
                if product_dir in path_parts:
                    try:
                        product_id_index = path_parts.index(product_dir) + 1
                        if product_id_index < len(path_parts):
                            product_id = path_parts[product_id_index]

                            if product_id in product_map:
                                product_name = product_map[product_id]
                                sanitized_name = sanitize_filename(product_name)
                                file_extension = os.path.splitext(file)[1]

                                # Handle multiple images for the same product
                                count = renamed_counts.get(sanitized_name, 0) + 1
                                renamed_counts[sanitized_name] = count

                                if count > 1:
                                    new_filename = f"{sanitized_name}_{count}{file_extension}"
                                else:
                                    new_filename = f"{sanitized_name}{file_extension}"

                                old_path = os.path.join(root, file)
                                new_path = os.path.join('.', new_filename) # Move to root

                                try:
                                    shutil.move(old_path, new_path)
                                    print(f"Moved '{old_path}' to '{new_path}'")
                                except Exception as e:
                                    print(f"Could not move {old_path}: {e}")

                    except ValueError:
                        # 'product' not in path, should not happen with os.walk on product_dir
                        continue


if __name__ == "__main__":
    process_products()
