def read_dep(dep, depth=0):
    nouns = []
    all_entities = []
    last_word_dict = {}

    # Select nouns and adjectives
    nouns = []
    # Verbs
    verbs = []
    # Everything else preposition, etc
    all_entities = []

    add_noun = nouns.append
    add_verb = verbs.append
    add_all_entities = all_entities.append

    def process_pos_tag(word_tag):
        word,pos_tag = word_tag
        p_noun = None
        p_verb = None
        p_other = None
        if pos_tag.startswith('NN') or pos_tag.startswith('JJ'):
           p_noun = ['noun', [word_tag]]
        elif pos_tag.startswith('VB'):
           p_verb = ['verb', [word_tag]]
        else:
           p_other = ['other', [word_tag]]
        add_noun(p_noun)
        add_verb(p_verb)
        add_all_entities(p_other)
    list(map(process_pos_tag, dep.pos()))

    last = None
    # Counter for tracking entities that can be safely removed that were merged with another entity
    i = 0
    drop_list = []
    append = drop_list.append
    for noun,verb,other in zip(nouns, verbs, all_entities):
        node = noun or verb or other

        if last:
            if last == 'noun' and noun:
                nouns[i-1][1].extend(node[1])
                drop_list.append(i)
            elif last == 'verb' and verb:
                verbs[i-1][1].extend(node[1])
                drop_list.append(i)
            elif last == 'other' and other:
                all_entities[i-1][1].extend(node[1])
                drop_list.append(i)
        last = node[0]
        i += 1

    drop_list = drop_list[::-1]
    list(map(nouns.pop, drop_list))
    list(map(verbs.pop, drop_list))
    list(map(all_entities.pop, drop_list))

    tokens = [noun or verb or other for noun,verb,other in zip(nouns,verbs,all_entities)]
    return tokens
