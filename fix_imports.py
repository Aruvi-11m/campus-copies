import os
import re

backend_dir = "/Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus_copies/backend"

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace from ..utils.pdf_utils import ... -> from utils.pdf_utils import ...
    content = re.sub(r'^from \.\.(\w+)', r'from \1', content, flags=re.MULTILINE)
    
    # Replace from .. import models, schemas, dependencies -> import models, schemas, dependencies
    # Wait, the prompt specifically says "scan every Python file for remaining relative imports beginning with 'from .' and fix them"
    # Actually, if it says `from .. import models`, it can be `import models`. Or `import models, schemas...`
    # Let's replace `from .. import ` with `import `? No, it's safer to just do `import ...`.
    content = re.sub(r'^from \.\. import (.*)', r'import \1', content, flags=re.MULTILINE)

    # Replace from .database import ... -> from database import ...
    content = re.sub(r'^from \.(\w+) import ', r'from \1 import ', content, flags=re.MULTILINE)
    
    # Replace from . import models, schemas -> import models, schemas
    content = re.sub(r'^from \. import (.*)', r'import \1', content, flags=re.MULTILINE)

    with open(filepath, 'w') as f:
        f.write(content)

for root, dirs, files in os.walk(backend_dir):
    if 'venv' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

print("Fixed imports")
