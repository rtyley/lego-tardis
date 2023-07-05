from hasher import sha256

def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value


class Passphrase:
    adjectives = ["GOOD", "BAD", "DRY", "WET", "FUN", "SLY", "HOT", "TOP"]
    nouns = ["ANT", "BEE", "CAT", "DOG", "FOX", "PIG", "YAK", "WOLF"]

    def __init__(self, hashBytes):
        num = reduce(lambda a, b: a ^ b, hashBytes)
        adjective_index = num % len(self.adjectives)
        noun_index = (num // len(self.adjectives)) % len(self.nouns)
        self.wordIndices = [adjective_index, noun_index]
        self.words = [Passphrase.adjectives[adjective_index], Passphrase.nouns[noun_index]]
        self.fullText = ' '.join(self.words)

    def __repr__(self):
        return self.fullText


class TreasurePassphrases:

    def __init__(self, salts):
        self.numSalts = len(salts)
        print(f'numSalts={self.numSalts}')
        self.salts = salts

    def passphraseFor(self, passphrase_epoch):
        salt_index = passphrase_epoch % self.numSalts
        salt = self.salts[salt_index]
        if salt is None:
            return None
        else:
            h = sha256(salt.encode('utf-8'))
            h.update(passphrase_epoch.to_bytes(8, 'big'))
            return Passphrase(h.digest())
