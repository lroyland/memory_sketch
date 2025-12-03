from dotenv import load_dotenv
load_dotenv()
import replicate, os
import sys
from replicate.exceptions import ModelError

print('token?', bool(os.getenv('REPLICATE_API_TOKEN')), file=sys.stderr)
print('Starting replicate run...', file=sys.stderr)

try:
    print('Calling replicate.run with file object...', file=sys.stderr)
    with open("test_selfie.jpg", "rb") as f:
        # Try with full model path including version
        out = replicate.run(
            "fofr/sdxl-multi-controlnet-lora:89eb212b3d1366a83e949c12a4b45dfe6b6b313b594cb8268e864931ac9ffb16",
            input={
                "image": f,
                "control_type": "lineart",
                "prompt": "loose and childish composite sketch, rough lineart, uneven pencil strokes, simplified facial geometry, black and white pencil ",
              
                "style_strength": 0.7,
                "safety_tolerance": 2,  # Try to reduce NSFW filtering (0-6, higher = less strict)
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
except ModelError as e:
    error_msg = str(e)
    if "NSFW" in error_msg:
        print('❌ NSFW Content Detected', file=sys.stderr)
        print('   The model flagged the image. This can be a false positive.', file=sys.stderr)
        print('   Try:', file=sys.stderr)
        print('   1. Using a different image', file=sys.stderr)
        print('   2. Running again (sometimes works on retry)', file=sys.stderr)
        print('   3. Adjusting safety_tolerance parameter', file=sys.stderr)
    else:
        print(f'ModelError: {error_msg}', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
