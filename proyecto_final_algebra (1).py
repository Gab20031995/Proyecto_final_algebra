# -*- coding: utf-8 -*-
"""Proyecto_final_Algebra.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1C4MptMPENu1-j4D1H814SBSROVwITZ5o

#  Detección de Neumonía en Imágenes Médicas con álgebra lineal

# Carga de datos y J.SON con API de KAGGLE
"""

from google.colab import files

# Sube tu archivo kaggle.json
files.upload()

# Mueve el archivo kaggle.json a la ubicación correcta
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!pip install kaggle

# Descarga el conjunto de datos usando la API de Kaggle
!kaggle datasets download -d paultimothymooney/chest-xray-pneumonia

"""# Desconprime el .zip de los datos


"""

!unzip chest-xray-pneumonia.zip -d datos_pneumonia

"""# 2

"""

!ls datos_pneumonia

!ls datos_pneumonia/chest_xray

import os

# Ruta al directorio donde se extrajeron los datos
data_dir = "datos_pneumonia"

# Función para mostrar la estructura de carpetas
def mostrar_estructura_carpetas(data_dir):
    for root, dirs, files in os.walk(data_dir):
        if dirs:
            print(f"Directorio: {root}")
            print(f"Subdirectorios: {dirs}")
            print("--------------------")

# Mostrar la estructura de carpetas
mostrar_estructura_carpetas(data_dir)

from tqdm import tqdm
import cv2
import os
import numpy as np

def cargar_datos(data_dir, classes):
    data = []
    errores = 0

    for clase in classes:
        path = os.path.join(data_dir, clase)
        class_num = classes.index(clase)

        for img in tqdm(os.listdir(path), desc=f'Cargando {clase}'):
            try:
                img_array = cv2.imread(os.path.join(path, img), cv2.IMREAD_GRAYSCALE)
                img_resized = cv2.resize(img_array, (128, 128))
                # Normalizar los valores de píxeles entre 0 y 1
                img_resized = img_resized / 255.0
                data.append([img_resized, class_num])
            except Exception as e:
                errores += 1
                print(f"Error al procesar {clase}/{img}: {str(e)}")

    print(f"Total de errores: {errores}")
    return np.array(data)

# Ejemplo de uso
data_dir = 'datos_pneumonia/chest_xray/train'  # Ajusta la ruta según tu estructura
classes = ['NORMAL', 'PNEUMONIA']

data_val = 'datos_pneumonia/chest_xray/val'


# Cargar datos
datos = cargar_datos(data_dir, classes)
datos_val = cargar_datos(data_val, classes)

mostrar_estructura_carpetas(data_dir)

"""# Importación de los datos y aumento


"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Directorio principal
base_dir = '/content/datos_pneumonia/chest_xray'

# Directorio de entrenamiento
train_dir = os.path.join(base_dir, 'train')

# Subdirectorios
subdirs = ['PNEUMONIA', 'NORMAL']

# Función para cargar y preprocesar imágenes
def load_and_preprocess_images(base_dir, subdir, label, num_images=5, target_size=(224, 224)):
    directory = os.path.join(base_dir, subdir)
    fig, axes = plt.subplots(1, num_images, figsize=(15, 3))

    for i, filename in enumerate(os.listdir(directory)[:num_images]):
        img_path = os.path.join(directory, filename)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Redimensionar la imagen
        img = cv2.resize(img, target_size)

        # Normalizar la imagen
        img = img / 255.0

        axes[i].imshow(img)
        axes[i].set_title(label)
        axes[i].axis('off')

    plt.show()

# Aumento de datos utilizando ImageDataGenerator de TensorFlow
def data_augmentation(base_dir, subdir, label, num_images=5, target_size=(224, 224)):
    directory = os.path.join(base_dir, subdir)

    # Configuración del generador de imágenes
    datagen = ImageDataGenerator(
        rotation_range=40,#cambio
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    fig, axes = plt.subplots(1, num_images, figsize=(15, 3))

    for i, filename in enumerate(os.listdir(directory)[:num_images]):
        img_path = os.path.join(directory, filename)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Redimensionar la imagen
        img = cv2.resize(img, target_size)

        # Normalizar la imagen
        img = img / 255.0

        # Aumento de datos
        img = np.expand_dims(img, axis=0)
        augmented_img = datagen.flow(img).next()[0]

        axes[i].imshow(augmented_img)
        axes[i].set_title(label)
        axes[i].axis('off')

    plt.show()

# Cargar y preprocesar imágenes de PNEUMONIA
load_and_preprocess_images(train_dir, subdirs[0], 'Pneumonia')

# Cargar y preprocesar imágenes de NORMAL
load_and_preprocess_images(train_dir, subdirs[1], 'Normal')
print("-------------------------------------------------------------------------")
print("Aumento de la data")
# Aumento de datos para PNEUMONIA
data_augmentation(train_dir, subdirs[0], 'Pneumonia')

# Aumento de datos para NORMAL
data_augmentation(train_dir, subdirs[1], 'Normal')

"""# CNN (Entrenamiento)"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Directorio principal
base_dir = '/content/datos_pneumonia/chest_xray'

# Directorio de entrenamiento
train_dir = os.path.join(base_dir, 'train')

# Subdirectorios
subdirs = ['PNEUMONIA', 'NORMAL']

# Configuración del modelo CNN
model = Sequential()

model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)))
model.add(MaxPooling2D(2, 2))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(2, 2))

model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(2, 2))

model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(2, 2))

model.add(Flatten())

model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))

model.add(Dense(1, activation='sigmoid'))  # Binary classification

# Compilar el modelo
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Crear generadores de datos para entrenamiento y validación
train_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

# Entrenar el modelo
history = model.fit(train_generator, epochs=10, verbose=1)

# Visualizar resultados del entrenamiento
plt.plot(history.history['accuracy'])
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.show()

"""# PCA 1"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import backend as K
from sklearn.decomposition import PCA

# Obtener las representaciones intermedias de la primera capa convolucional
get_intermediate_output = K.function([model.layers[0].input], [model.layers[0].output])
batch = train_generator.next()
input_data = batch[0]
label_data = batch[1]

conv1_output = get_intermediate_output([input_data])[0]

# Aplanar los datos para que sean compatibles con PCA
conv1_output_flat = conv1_output.reshape(conv1_output.shape[0], -1)

# Aplicar PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(conv1_output_flat)

# Visualizar los resultados de PCA
plt.scatter(pca_result[:, 0], pca_result[:, 1], c=label_data, cmap='viridis')
plt.title('PCA')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

"""# CNN (Evaluando)"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Directorio principal
base_dir = 'datos_pneumonia/chest_xray/chest_xray/val'

# Subdirectorios
subdirs = ['PNEUMONIA', 'NORMAL']

# Crear generadores de datos para entrenamiento y validación
train_datagen = ImageDataGenerator(rescale=1./255)
val_generator = train_datagen.flow_from_directory(
    base_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    shuffle=False  # Para que las imágenes y las predicciones estén en el mismo orden
)

# Hacer predicciones
predictions = model.predict(val_generator, verbose=1)

# Obtener imágenes y etiquetas reales
images, labels = next(val_generator)

# Imprimir las imágenes junto con las etiquetas reales y predicciones
for i in range(len(images)):
    img = images[i]
    label = labels[i]
    prediction = predictions[i]

    # Convertir la etiqueta y la predicción a texto
    label_text = 'PNEUMONIA' if label == 1 else 'NORMAL'
    prediction_text = 'PNEUMONIA' if prediction > 0.5 else 'NORMAL'

    # Mostrar la imagen con la etiqueta real y la predicción
    plt.imshow(img)
    plt.title(f"Real: {label_text}, Predicción: {prediction_text}")
    plt.show()

"""# ROC"""

from sklearn.metrics import classification_report, roc_curve, auc
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# Directorio de las imágenes de prueba
test_dir = 'datos_pneumonia/chest_xray/chest_xray/val'

# Crear generador de datos para pruebas
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    shuffle=False
)

# Obtener las etiquetas verdaderas
y_true = test_generator.classes

# Obtener las predicciones del modelo
y_pred = model.predict(test_generator).ravel()

# Calcular las métricas de evaluación
report = classification_report(y_true, y_pred > 0.5, target_names=['NORMAL', 'PNEUMONIA'])
print(report)

# Calcular la curva ROC
fpr, tpr, thresholds = roc_curve(y_true, y_pred)
roc_auc = auc(fpr, tpr)

# Visualizar la curva ROC
plt.figure()
plt.plot(fpr, tpr, color='darkorange', label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

"""# Modelo de simulación de evolución de células cancerígenas con ecuaciones diferenciales

- $\frac{dS}{dt} = r * S - β * S * C - γ * S $

- $\frac{d S}{dt} = a * C - β * S * C $

un modelo de simulación de la evolución de células cancerígenas utilizando ecuaciones diferenciales puede ser un proyecto complejo, pero te proporcionaré un esbozo básico que puedes utilizar como punto de partida. Este ejemplo asume un enfoque simplificado y no tiene en cuenta muchos aspectos importantes de la biología real del cáncer. Asegúrate de ajustar y expandir este modelo según sea necesario para satisfacer tus requisitos específicos.

Primero, definamos algunas variables y parámetros:

- S(t): Cantidad de células sanas en el tiempo
- C(t): Cantidad de células cancerígenas en el tiempo
- r: Factor de recuperación
- α: Tasa de muerte de las células cancerígenas
- β: Tasa de conversión de células cancerígenas a células sanas
- γ: Tasa de muerte natural de las células sanas
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual

# Definir el sistema de ecuaciones diferenciales
def modelo_celular(y, t, alpha, beta, gamma, delta):
    dydt = [
        alpha * y[0] - beta * y[0] * y[1],
        xelta * y[0] * y[1] - gamma * y[1]
    ]
    return dydt

# Función para simular el modelo y visualizar resultados
def simular_modelo(alpha, beta, gamma, delta, tiempo_final):
    # Condiciones iniciales
    y0 = [0.1, 0.1]

    # Definir el tiempo
    tiempo = np.linspace(0, tiempo_final, 100)

    # Resolver las ecuaciones diferenciales
    solucion = odeint(modelo_celular, y0, tiempo, args=(alpha, beta, gamma, delta))

    # Visualizar la solución
    plt.figure(figsize=(10, 6))
    plt.plot(tiempo, solucion[:, 0], label='Células sanas')
    plt.plot(tiempo, solucion[:, 1], label='Células cancerígenas')
    plt.title('Simulación de la evolución de células cancerígenas en la piel')
    plt.xlabel('Tiempo')
    plt.ylabel('Proporción de células')
    plt.legend()
    plt.grid(True)
    plt.show()

# Sliders interactivos
alpha_slider = widgets.FloatSlider(value=0.1, min=0, max=1, step=0.01, description='Alpha:')
beta_slider = widgets.FloatSlider(value=0.02, min=0, max=1, step=0.01, description='Beta:')
gamma_slider = widgets.FloatSlider(value=0.1, min=0, max=1, step=0.01, description='Gamma:')
delta_slider = widgets.FloatSlider(value=0.01, min=0, max=1, step=0.01, description='Delta:')
tiempo_final_slider = widgets.FloatSlider(value=10, min=1, max=50, step=1, description='Tiempo Final:')

# Interfaz interactiva
interact(
    simular_modelo,
    alpha=alpha_slider,
    beta=beta_slider,
    gamma=gamma_slider,
    delta=delta_slider,
    tiempo_final=tiempo_final_slider
);

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import ipywidgets as widgets
from ipywidgets import interact

# Definir el sistema de ecuaciones diferenciales
def modelo_celular(y, t, alpha, beta, gamma, delta):
    """
    Ecuaciones del modelo de evolución de células cancerígenas en la piel.

    Parámetros:
    - y: Lista de variables de estado [Células sanas, Células cancerígenas]
    - t: Tiempo
    - alpha, beta, gamma, delta: Parámetros del modelo

    Retorna:
    Lista de derivadas de las variables de estado.
    """
    dydt = [
        alpha * y[0] - beta * y[0] * y[1],
        delta * y[0] * y[1] - gamma * y[1]
    ]
    return dydt

# Función para simular el modelo y visualizar resultados
def simular_modelo(alpha, beta, gamma, delta, tiempo_final):
    """
    Simula el modelo de evolución de células cancerígenas y visualiza los resultados.

    Parámetros:
    - alpha, beta, gamma, delta: Parámetros del modelo
    - tiempo_final: Tiempo total de simulación

    Retorna:
    Gráficos de la evolución de células sanas y cancerígenas en el tiempo.
    """
    # Condiciones iniciales
    y0 = [0.1, 0.1]

    # Definir el tiempo
    tiempo = np.linspace(0, tiempo_final, 100)

    # Resolver las ecuaciones diferenciales
    solucion = odeint(modelo_celular, y0, tiempo, args=(alpha, beta, gamma, delta))

    # Visualizar la solución
    plt.figure(figsize=(10, 6))
    plt.plot(tiempo, solucion[:, 0], label='Células sanas', color='green')
    plt.plot(tiempo, solucion[:, 1], label='Células cancerígenas', color='red')
    plt.title('Simulación de la evolución de células cancerígenas en la piel')
    plt.xlabel('Tiempo')
    plt.ylabel('Proporción de células')
    plt.legend()
    plt.grid(True)
    plt.show()

# Sliders interactivos
alpha_slider = widgets.FloatSlider(value=0.1, min=0, max=1, step=0.01, description='Alpha:')
beta_slider = widgets.FloatSlider(value=0.02, min=0, max=1, step=0.01, description='Beta:')
gamma_slider = widgets.FloatSlider(value=0.1, min=0, max=1, step=0.01, description='Gamma:')
delta_slider = widgets.FloatSlider(value=0.01, min=0, max=1, step=0.01, description='Delta:')
tiempo_final_slider = widgets.FloatSlider(value=10, min=1, max=50, step=1, description='Tiempo Final:')

# Interfaz interactiva
interact(
    simular_modelo,
    alpha=alpha_slider,
    beta=beta_slider,
    gamma=gamma_slider,
    delta=delta_slider,
    tiempo_final=tiempo_final_slider
);

