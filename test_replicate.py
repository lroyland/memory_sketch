from dotenv import load_dotenv
load_dotenv()
import replicate, os
import sys

print('token?', bool(os.getenv('REPLICATE_API_TOKEN')), file=sys.stderr)
print('Starting replicate run...', file=sys.stderr)

try:
    print('Calling replicate.run with file object...', file=sys.stderr)
    with open("test_selfie.png", "rb") as f:
        # Try with full model path including version
        out = replicate.run(
            "adirik/t2i-adapter-sdxl-sketch:3a14a915b013decb6ab672115c8bced7c088df86c2ddd0a89433717b9ec7d927",
            input={
                "image": f,  # This model might use "sketch" instead of "image"
                "prompt": "crude police composite sketch, pencil on rough paper, low detail",
                "num_inference_steps": 5,
                "guidance_scale": 6,
            },
        )
    print('Result type:', type(out))
    if isinstance(out, list):
        print('Result list length:', len(out))
        for i, item in enumerate(out):
            print(f'Item {i}:', item)
            if hasattr(item, 'url'):
                print(f'  URL: {item.url}')
            elif hasattr(item, '__str__'):
                print(f'  String: {str(item)}')
    else:
        print('Result:', out)
        if hasattr(out, 'url'):
            print('URL:', out.url)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
