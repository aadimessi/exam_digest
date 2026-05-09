!pip install transformers datasets accelerate evaluate -q
import json
import pandas as pd
import numpy as np
import re
import torch

from google.colab import files

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

from datasets import Dataset
uploaded = files.upload()

TRAIN_FILE = list(uploaded.keys())[0]

with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print(df.head())

print(df.columns)
CODE_COLUMN = "code"
LABEL_COLUMN = "labels"

df = df[[CODE_COLUMN, LABEL_COLUMN]]
df.dropna(inplace=True)
df[CODE_COLUMN] = df[CODE_COLUMN].astype(str)
df[LABEL_COLUMN] = df[LABEL_COLUMN].astype(str)
print(df.shape)
print(df[LABEL_COLUMN].value_counts())
def preprocess_code(code):
    code = str(code)
    code = re.sub(r"\s+", " ", code)
    return code

df[CODE_COLUMN] = df[CODE_COLUMN].apply(preprocess_code)
label_encoder = LabelEncoder()

df[LABEL_COLUMN] = label_encoder.fit_transform(df[LABEL_COLUMN])

num_classes = len(label_encoder.classes_)

print("\nClasses:")
print(label_encoder.classes_)

print("\nNumber of Classes:", num_classes)
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df[CODE_COLUMN],
    df[LABEL_COLUMN],
    test_size=0.2,
    random_state=42,
    stratify=df[LABEL_COLUMN]
)
MODEL_NAME = "microsoft/codebert-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
train_encodings = tokenizer(
    list(train_texts),
    truncation=True,
    padding=True,
    max_length=256
)

test_encodings = tokenizer(
    list(test_texts),
    truncation=True,
    padding=True,
    max_length=256
)
class CodeSmellDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):

        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):

        item = {
            key: torch.tensor(val[idx])
            for key, val in self.encodings.items()
        }

        item["labels"] = torch.tensor(self.labels.iloc[idx])

        return item

    def __len__(self):

        return len(self.labels)
train_dataset = CodeSmellDataset(
    train_encodings,
    train_labels.reset_index(drop=True)
)

test_dataset = CodeSmellDataset(
    test_encodings,
    test_labels.reset_index(drop=True)
)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_classes
)
def compute_metrics(pred):

    labels = pred.label_ids

    preds = pred.predictions.argmax(-1)

    accuracy = accuracy_score(labels, preds)

    precision = precision_score(
        labels,
        preds,
        average='weighted'
    )

    recall = recall_score(
        labels,
        preds,
        average='weighted'
    )

    f1 = f1_score(
        labels,
        preds,
        average='weighted'
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }
training_args = TrainingArguments(

    output_dir="./results",

    num_train_epochs=4,

    per_device_train_batch_size=8,

    per_device_eval_batch_size=8,

    logging_steps=100,

    learning_rate=2e-5,

    weight_decay=0.01,

    warmup_ratio=0.1,

    fp16=torch.cuda.is_available()
)
trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=test_dataset,

    compute_metrics=compute_metrics
)
trainer.train()
results = trainer.evaluate()

print("\nEvaluation Results:")
print(results)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

predictions = trainer.predict(test_dataset)

y_pred = np.argmax(predictions.predictions, axis=1)

y_true = test_labels.reset_index(drop=True)

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true,
    y_pred,
    average='weighted'
)

recall = recall_score(
    y_true,
    y_pred,
    average='weighted'
)

f1 = f1_score(
    y_true,
    y_pred,
    average='weighted'
)

print(f"\nAccuracy  : {accuracy*100:.2f}%")

print(f"Precision : {precision*100:.2f}%")

print(f"Recall    : {recall*100:.2f}%")

print(f"F1 Score  : {f1*100:.2f}%")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=label_encoder.classes_
    )
)

cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(16,12))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues'
)

plt.title("Confusion Matrix")

plt.xlabel("Predicted Labels")

plt.ylabel("True Labels")

plt.show()
model.save_pretrained("codebert_smell_model")

tokenizer.save_pretrained("codebert_smell_model")
