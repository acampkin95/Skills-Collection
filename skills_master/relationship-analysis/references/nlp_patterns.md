# NLP Patterns Reference

## Sentiment Analysis

Uses TextBlob for sentiment scoring:

| Metric | Range | Interpretation |
|--------|-------|----------------|
| Polarity | -1.0 to 1.0 | Negative ↔ Positive |
| Subjectivity | 0.0 to 1.0 | Objective ↔ Subjective |

```python
from textblob import TextBlob
blob = TextBlob(text)
polarity = blob.sentiment.polarity
subjectivity = blob.sentiment.subjectivity
```

## Message Analysis Patterns

### Love/Affection Words
```python
love_pattern = re.compile(
    r'\b(love|adore|miss|cherish|treasure|heart|darling|'
    r'sweetheart|babe|baby|honey)\b', re.I
)
```

### Negative Words
```python
negative_pattern = re.compile(
    r'\b(hate|angry|upset|frustrated|annoyed|disappointed|'
    r'hurt|sad|mad|furious|disgusted)\b', re.I
)
```

### Affection Words
```python
affection_pattern = re.compile(
    r'\b(hug|kiss|cuddle|snuggle|hold|embrace|xoxo|mwah)\b', re.I
)
```

### Apology Words
```python
apology_pattern = re.compile(
    r'\b(sorry|apologize|apologies|forgive|my bad|my fault)\b', re.I
)
```

### Gratitude Words
```python
gratitude_pattern = re.compile(
    r'\b(thank|thanks|grateful|appreciate|thx)\b', re.I
)
```

### Emoji Detection
```python
emoji_pattern = re.compile(
    r'[\U0001F300-\U0001F9FF'
    r'\U0001FA00-\U0001FA6F'
    r'\U0001FA70-\U0001FAFF'
    r'\U00002702-\U000027B0'
    r'\U0001F600-\U0001F64F]'
)
```

## Attachment Style Markers

### Anxious-Preoccupied
```python
anxious_patterns = [
    r'\b(please|plz)\b',
    r'\bsorry\b',
    r'\bworried\b',
    r'\bneed you\b',
    r'\bmiss you\b',
    r"don't leave\b",
    r'\bpromise me\b',
    r'\bare you mad\b',
    r'\bdo you still\b',
    r'\bwhy aren\'t you\b',
    r'\banswer me\b'
]
```

### Dismissive-Avoidant
```python
avoidant_patterns = [
    r'\bneed space\b',
    r'\bbusy\b',
    r'\blater\b',
    r'\bfine\b',
    r'\bwhatever\b',
    r'\bidk\b',
    r'\bnot now\b',
    r'\bleave me\b',
    r'\balone\b',
    r'\bback off\b',
    r'\bchill\b'
]
```

### Secure
```python
secure_patterns = [
    r'\bunderstand\b',
    r'\bappreciate\b',
    r'\btogether\b',
    r'\btrust\b',
    r'\bcommunicate\b',
    r'\bcompromise\b',
    r'\bsupport\b',
    r'\bteam\b',
    r'\bpartner\b',
    r'\bwe can\b'
]
```

### Controlling
```python
controlling_patterns = [
    r'\byou should\b',
    r'\byou need to\b',
    r'\bwhy did you\b',
    r'\bwhere are you\b',
    r'\bwho are you with\b',
    r'\bwhy didn\'t you\b',
    r'\byou always\b',
    r'\byou never\b'
]
```

## Conflict Detection

```python
conflict_patterns = [
    r'\byou always\b',
    r'\byou never\b',
    r'\bi\'m done\b',
    r'\bhurt\b',
    r'\bangry\b',
    r'\bfurious\b',
    r'\bhate\b',
    r'\bsick of\b',
    r'\btired of\b',
    r'\bcan\'t believe\b',
    r'\bwhat the\b',
    r'\bwtf\b'
]
```

## Third-Party Extraction

### Name Context Patterns
```python
name_patterns = [
    r'\bwith ([A-Z][a-z]{2,12})\b',
    r'\btold ([A-Z][a-z]{2,12})\b',
    r'\b([A-Z][a-z]{2,12})\'s\b',
    r'\bmy friend ([A-Z][a-z]{2,12})\b',
    r'\bsaw ([A-Z][a-z]{2,12})\b',
    r'\bfrom ([A-Z][a-z]{2,12})\b',
    r'\bto ([A-Z][a-z]{2,12})\b',
    r'\b([A-Z][a-z]{2,12}) said\b',
    r'\b([A-Z][a-z]{2,12}) and I\b'
]
```

### Exclusion List
Common words that match name patterns but aren't names:
```python
exclude = {
    'But', 'The', 'That', 'This', 'What', 'When', 'Where', 'Why', 'How',
    'Just', 'Like', 'Love', 'Loved', 'Have', 'Has', 'Had', 'Was', 'Were',
    'Yes', 'Yeah', 'Yea', 'Nope', 'Sure', 'Maybe', 'Good', 'Great', 'Nice',
    'Thanks', 'Thank', 'Sorry', 'Please', 'Hello', 'Hey', 'Morning', 'Night',
    'Today', 'Tomorrow', 'Yesterday',
    # Days/months
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    'January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December',
    # Fillers
    'Also', 'Well', 'Still', 'Even', 'Much', 'Very', 'Really',
    'Actually', 'Probably', 'Definitely',
    # Gerunds
    'Going', 'Coming', 'Getting', 'Being', 'Doing', 'Having', 'Making',
    'Thinking', 'Feeling', 'Looking', 'Waiting', 'Working', 'Talking'
}
```

### Relationship Terms
```python
relationship_terms = [
    'mum', 'mom', 'mother', 'dad', 'father',
    'brother', 'sister', 'friend', 'friends',
    'therapist', 'counselor', 'doctor', 'boss',
    'ex', 'coworker', 'colleague'
]
```

## Linguistic Markers

### I/You/We Statement Detection
```python
i_statements = re.compile(r'\bI\s+(am|feel|think|want|need|believe)\b', re.I)
you_statements = re.compile(r'\bYou\s+(are|should|need|always|never)\b', re.I)
we_statements = re.compile(r'\bWe\s+(can|should|are|will|need)\b', re.I)
```

### Question Detection
```python
has_question = '?' in text
```

### Emphasis Detection
```python
has_caps = bool(re.search(r'\b[A-Z]{3,}\b', text))  # ALL CAPS words
has_exclamation = '!' in text
repeated_chars = bool(re.search(r'(.)\1{2,}', text))  # soooo, nooo
```
