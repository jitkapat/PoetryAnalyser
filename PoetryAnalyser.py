import spacy# for tokenising words


def load_cmu_dict():
    """load CMU dict file and convert into a dictionary of words with phonological properties
    :returns: a nested dictionary, with each word as key and a dictionary of properties as value.
    """

    file = open("cmudict-0.7b")
    dictionary = {}
    for line in file:
        line = line.strip()
        word_pronun = line.split('  ')
        phoneme_list = word_pronun[-1].strip().split(' ')
        vowels = []
        consonants = []
        stress_count = 0
        stress_pattern = []
        stress_to_pattern = {'0': 0, '1': 1, '2': 1}
        for phoneme in phoneme_list:
            if phoneme[-1] in ['0', '1', '2']:
                vowels.append(phoneme[0:-2])
                stress_pattern.append(stress_to_pattern[phoneme[-1]])
                if phoneme[-1] in ['1', '2']:
                    stress_count += 1
            else:
                consonants.append(phoneme)
        dictionary[word_pronun[0]] = {'phoneme': word_pronun[-1].split(' '), 'consonant': consonants,
                                      'vowel': vowels, 'stress_pattern': stress_pattern}
    return dictionary


# Note: The classes other than analyse are used to collect data in a hierarchical fashion.
# In most cases , please refer to the Poem class or the Analyse class.
class Word:
    # A class for a single word in a poem
    # For keeping information about a word that will be used to check metre, rhyme and any possible other features
    def __init__(self, word, dict)
        self.word = str(word).upper()
        self.dict = dict
        self.phoneme = self.get_phoneme()
        self.first_phoneme = self.phoneme[0]
        self.final_phoneme = self.phoneme[-1]
        self.consonant = self.get_consonant()
        self.vowel = self.get_vowel()
        self.stress_pattern = self.get_stress_pattern()
        self.syllable = len(self.vowel)
        self.final_syllable = self.get_final_syllable()

    # all functions in this classes are used to retrieve data from existing dictionary extracted from CMU dict
    def get_phoneme(self):
        if self.word in self.dict:
            return self.dict[self.word]['phoneme']

    def get_consonant(self):
        if self.word in self.dict:
            return self.dict[self.word]['consonant']

    def get_vowel(self):
        if self.word in self.dict:
            return self.dict[self.word]['vowel']

    def get_stress_pattern(self):
        if self.word in self.dict:
            return self.dict[self.word]['stress_pattern']

    def get_final_syllable(self):
        if self.final_phoneme in self.vowel:
            return self.final_phoneme
        else:
            result = self.vowel[-1]+self.final_phoneme
            return result


class Poetry:
    # Used to contain common functions for Line and Poem classes
    def __init__(self, line, dict):
        pass

    def if_rhyme(self, word1, word2):
        """
        checks whether word1 and word2 rhymes
        """
        word1 = Word(word1, self.dict)
        word2 = Word(word2, self.dict)
        if word1.final_syllable == word2.final_syllable:
            return True
        else:
            return False

    def if_alliterate(self, word1, word2):
        """
        checks whether word1 and word2 alliterates
        """
        word1 = Word(word1, self.dict)
        word2 = Word(word2, self.dict)
        if word1.first_phoneme == word2.first_phoneme:
            return True
        else:
            return False


class Line(Poetry):
    # A class for a single line in a poem
    # Contains data that will be used to analyse the poem's metre (single line's metre) and rhyme
    # Each word in the line will be collected using class Word
    def __init__(self, line, dict):
        self.nlp = spacy.load('en', disable=['parser', 'ner'])
        self.line = line
        self.dict = dict
        self.words = self.get_words()
        self.stress_pattern = self.get_stress_pattern()
        self.metre = self.get_metre()
        self.final_word = str(self.words[-1])

    def get_words(self):
        """
        tokenises inputted line with spacy and collect the tokens
        """
        tokenised_line = self.nlp(self.line)
        result = []
        for token in tokenised_line:
            if token.pos_ != 'PUNCT':
                result.append(token)
        return result

    def get_stress_pattern(self):
        """
        retrieves stress pattern data from Word class and combine each word into a pattern of a single line 
        """
        result = []
        for word in self.words:
            word2 = Word(word, self.dict)
            adjusted_stress_pattern = []
            if word.pos_ not in ["NOUN", "VERB", "ADJ", "ADV"]:
                for stress in word2.stress_pattern:
                    adjusted_stress_pattern.append(0)
            else:
                for stress in word2.stress_pattern:
                    adjusted_stress_pattern.append(stress)
            result += adjusted_stress_pattern
        return result

    def get_metre(self):
        """
        uses stress pattern of the line and convert it into recognised metres
        """
        result = []
        syllable = len(self.stress_pattern)
        num_to_name = {1: "mono", 2: "di", 3: "tri",
                       4: "tetra", 5: "penta", 6: "hexa",
                       7: "hepta", 8: "octa"}
        foot_to_metre = {'01': 'iambic ', '10': 'trochaic ', '11': 'spondaic ',
                         '00': 'unknown ', '100': 'dactylic', '001': 'anapestic ',
                         '101': 'unknown ', '110': 'unknown ', '011': 'unknown ',
                         '010': 'unknown ', '000': 'unknown '}

        if syllable % 2 == 0:
            foot_type = {}
            for i in range(0, syllable, 2):
                current_foot = ''.join([str(self.stress_pattern[i]), str(self.stress_pattern[i+1])])
                foot_type[foot_to_metre[current_foot]] = 0
            for i in range(0, syllable, 2):
                current_foot = ''.join([str(self.stress_pattern[i]), str(self.stress_pattern[i + 1])])
                foot_type[foot_to_metre[current_foot]] += 1
            result_foot = list(foot_type)[0]
            metre = result_foot+num_to_name[round(syllable/2)]+'metre'
            result.append(metre)

        if syllable % 3 == 0:
            foot_type = {}
            for i in range(0, syllable, 3):
                current_foot = ''.join([str(self.stress_pattern[i]),
                                        str(self.stress_pattern[i + 1]),
                                        str(self.stress_pattern[i + 2])])
                foot_type[foot_to_metre[current_foot]] = 0
            for i in range(0, syllable, 3):
                current_foot = ''.join([str(self.stress_pattern[i]),
                                        str(self.stress_pattern[i + 1]),
                                        str(self.stress_pattern[i + 2])])
                foot_type[foot_to_metre[current_foot]] = 0
            result_foot = list(foot_type)[0]
            metre = result_foot + num_to_name[round(syllable / 2)] + 'metre'
            result.append(metre)

        else:
            if len(result) == 0:
                result.append('free metre')
        return result[0]


class Poem(Poetry):
    # Used to collect data from a file, convert it line by line into class Line to collect deeper data.
    # Most analyses occur in this class.
    # In cases of retrieving individual proponent's (line, word) data, please use this class's methods.

    def __init__(self, filename, dict):
        self.file = open(filename)
        self.dict = dict
        self.lines = self.get_lines()
        self.line_num = len(self.lines)
        self.metre = self.get_metre()
        self.rhyme_pattern = self.get_rhyme_pattern()
        self.file.close()

    def get_lines(self):
        "convert a single poem into lines"
        lines = []
        for line in self.file:
            if line != '\n':
                lines.append(Line(line.strip(), self.dict))
        return lines

    def get_metre(self):
        """
        retrieves the metre of each line and find the most common metre 
        """
        metre_dict = {}
        for line in self.lines:
            metre_dict[line.metre] = 0
        for line in self.lines:
            metre_dict[line.metre] += 1
        result = list(metre_dict)[0]
        return result

    def get_rhyme_pattern(self):
        """
        checks the final syllable of each line and convert into rhyme patterns
        """
        letter_list = 'A B C D E F G H J I K L M N O P Q R S T U V W X Y Z'.split(' ')
        letter_check = 'A B C D E F G H J I K L M N O P Q R S T U V W X Y Z'.split(' ')
        pattern_collection = [line for line in self.lines]
        for i, line in enumerate(pattern_collection):
            if line not in letter_check:
                current_final_word = line.final_word
                current_label = letter_list.pop(0)
                pattern_collection[i] = current_label
                for i2, line2 in enumerate(pattern_collection):
                    if line2 not in letter_check:
                        if self.if_rhyme(current_final_word, line2.final_word):
                            pattern_collection[i2] = current_label
        return ''.join(pattern_collection)


class Analyse:
    # The class that displays data from class Poem.
    # in most cases, just instantiating this class will suffice.
    def __init__(self, filename):
        self.filename = filename
        self.dict = load_cmu_dict()
        self.poem = Poem(self.filename, self.dict)
        print(self.filename+'\n')
        print("This poem has {} lines".format(self.poem.line_num))
        print("The poem's metre is " + self.poem.metre)
        print("The poem's rhyme pattern is " + self.poem.rhyme_pattern)
        print("\n")


# if __name__ == '__main__':
    # instantiate an object of Analyse class, using poem's filename as an argument.
    # poem = 'amazinggrace.txt'
    # Analyse(poem)


