from Magnet.settings import BASE_DIR
import os

CHUNK_RULE = r'''US:
    {<RB><JJ.*>}
    {<RB><VB.*>}
    {<NN.*><JJ.*>}
    {<NN.*><NN.*>}
    {<JJ.*><NN.*>}
    {<NN.*><PRP.*><NN.*>}
    {<VB.*><NN.*>}
    {<VB.*><PRP.*><NN.*>}
'''

CONTRACTIONS_PATTERNS = [
    (r'won\'t', 'will not'),
    (r'can\'t', 'cannot'),
    (r'i\'m', 'i am'),
    (r'ain\'t', 'is not'),
    (r'(\w+)\'ll', '\g<1> will'),
    (r'(\w+)n\'t', '\g<1> not'),
    (r'(\w+)\'ve', '\g<1> have'),
    (r'(\w+)\'s', '\g<1> is'),
    (r'(\w+)\'re', '\g<1> are'),
    (r'(\w+)\'d', '\g<1> would'),
]

GENERAL_PATTERNS = [
    (r'((www\.[\s]+)|(https?://[^\s]+))', '[URL]'),
    (r'@[^\s]+', 'Jhon'),
    (r'[\s]+', ' '),
    (r'#([^\s]+)', r'\1')
]

RTW_SPLIT_PATTERN = r'((RT|rt|via) @[A-Za-z0-9]+:? )'

CUSTOMPATTERNS = ["[U]", "[URL]"]

PURGE_TRESHOLD = 1

RAW_DATA_BASEPATH = os.path.join(BASE_DIR, "Core/data/raw")
PICKLED_DATA_BASEPATH = os.path.join(BASE_DIR, "Core/data/pickled")
