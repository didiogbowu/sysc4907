import sys
import os

package = os.path.dirname(os.path.realpath(__file__))
if package not in sys.path:
    sys.path.append(package)  # Must add sys.path for unittest to import properly
