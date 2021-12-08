import sys
from vc.service.helper.hash import HashHelper

if len(sys.argv) < 2:
    print('Usage: %s <plaintext>' % sys.argv[0])
    print()
    exit(9)

print(HashHelper.get(sys.argv[1]))
print()
