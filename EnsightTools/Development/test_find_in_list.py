import sys
sys.path.append('Y:\\Thelen\\EnsightTools\\EnsightTools')
import tools as T

list = ['frog','duck','cat','dog','pigeon','horse']

index = T.find_in_list('dog',list)

print "Found frog at index %d" % index
