import random
import sys
import time
from pathlib import Path

from tqdm import tqdm

from main import screenshot_path

file_paths = Path(screenshot_path).rglob('*.png')
for path in tqdm(list(file_paths), file=sys.stdout):
    time.sleep(random.randint(2, 5))
    print(path.name)
