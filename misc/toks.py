import io
import tokenize

for token in tokenize.tokenize(io.BytesIO(b"").readline):
    print(token)
