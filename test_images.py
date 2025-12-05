#!/usr/bin/env python3
"""Test the image generation service."""

import os
from services.images import generate_sketch_from_bytes

def test_image_generation():
    """Test generating a sketch from an image file."""
    test_image_path = "test_selfie.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Error: Test image '{test_image_path}' not found.")
        return
    
    print(f"Reading test image: {test_image_path}")
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    
    print("Generating sketch with new USER_TEXT...")
    print("Expected style: black-and-white pencil drawing, police sketch drawn by a child")
    try:
        sketch_url = generate_sketch_from_bytes(image_bytes)
        print("✓ Success! Generated sketch data URL (length:", len(sketch_url), "chars)")
        print("✓ Data URL starts with:", sketch_url[:50] + "...")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_generation()

