import json
import spacy
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags
from spacy.util import minibatch
from sklearn.model_selection import train_test_split
import random

with open("train_data2.json", "r") as f:
    TRAIN_DATA = json.load(f)



for text, ann in TRAIN_DATA:
    for start, end, label in ann["entities"]:
        if label == "PRONTUARIO":
            print(text[start:end])
quit()

train_data, dev_data = train_test_split(
    TRAIN_DATA,
    test_size=0.2,
    random_state=42
)





# Adicionando pontos para melhoria de modelo
nlp = spacy.load("pt_core_news_md")


#ner = nlp.add_pipe("ner")
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

labels = [
    "PACIENTE", "DATA_NASC", "PRONTUARIO", "SALA"
]

for label in labels:
    ner.add_label(label)

print(ner.labels)

# Desabilitando entidades originais do modelo
other_pipes = [
    pipe for pipe in nlp.pipe_names
    if pipe != "ner"
]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.resume_training()

#optimizer = nlp.initialize()




for epoch in range(30):
    random.shuffle(train_data)

    losses = {}

    batches = minibatch(train_data, size=8)

    for batch in batches:
        examples = []
        for text, annotations in batch:
            doc = nlp.make_doc(text)
            examples.append(Example.from_dict(doc, annotations))

        nlp.update(
            examples,
            sgd=optimizer,
            losses=losses,
            drop=0.2
        )
            
    print(f"Epoch {epoch}, {losses}")

    # Avaliação
    dev_examples = []
    for text, annotations in dev_data:
        dev_examples.append(
            Example.from_dict(
                nlp.make_doc(text),
                annotations
            )
        )
    
    scores = nlp.evaluate(dev_examples)

    print(
        f"Epoch {epoch} | "
        f"Loss={losses['ner']:.3f} | "
        f"F1={scores['ents_f']:.3f}"
    )
            
        #example = Example.from_dict(nlp.make_doc(text), annotations)
        #nlp.update([example], sgd=optimizer)


print(scores["ents_per_type"])

nlp.to_disk("modelo_medico_teste_dados")




"""
nlp = spacy.blank("pt")
ner = nlp.add_pipe("ner")

labels = [
    "PACIENTE", "DATA_NASC", "PRONTUARIO", "SALA"
]

for label in labels:
    ner.add_label(label)

optimizer = nlp.initialize()

for epoch in range(30):
    for text, annotations in TRAIN_DATA:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update([example], sgd=optimizer)

nlp.to_disk("modelo_medico_teste_dados3")
"""




'''
# Carrega uma linguagem "vazia" só para tokenização
nlp = spacy.blank("pt")

def validate_dataset(train_data):
    for i, (text, annot) in enumerate(train_data):
        print(f"\n=== Exemplo {i+1} ===")
        print(text)
        
        ents = annot.get("entities", [])
        doc = nlp(text)

        # Tenta converter offsets para tags BILUO
        try:
            tags = offsets_to_biluo_tags(doc, ents)
        except Exception as e:
            print("Erro de conversão:", e)
            continue

        # Verifica desalinhamentos
        misaligned = False
        for ent in ents:
            start, end, label = ent
            span = text[start:end]

            # Verifica consistência
            if span.strip() == "":
                misaligned = True
                print(f"⚠ ENTIDADE VAZIA: {ent}")

            # Verifica se spaCy reconhece esse recorte como tokens válidos
            try:
                span_doc = doc.char_span(start, end)
                if span_doc is None:
                    misaligned = True
                    print(f"❌ DESALINHADO: {ent}")
                    print(f"   Texto anotado: '{span}'")
            except:
                misaligned = True
                print(f"❌ DESALINHADO: {ent}")
                print(f"   Texto anotado: '{span}'")

        if not misaligned:
            print("✔ Todas as entidades alinhadas corretamente.")
        else:
            print("❗ Existem entidades desalinhadas — revise antes de treinar.")



validate_dataset(TRAIN_DATA)
'''
