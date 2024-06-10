import torch
from torchvision.transforms import transforms
from facenet_pytorch import InceptionResnetV1, MTCNN, extract_face

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def get_face_embedding(face):
    if face is None:
        return None

    face = transforms.Resize((160, 160))(face)
    face = transforms.ToTensor()(face).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = resnet(face)

    return embedding.cpu().numpy()
