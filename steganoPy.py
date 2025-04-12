from PIL import Image
import os, time, argparse

def open_image(img_path):
    img = Image.open(img_path)
    img = img.convert("RGB")
    pixels = list(img.getdata())

    return img, img.size, pixels

def text_to_bin(text):
    binary_list = [bit for c in text for bit in format(ord(c), '08b')]

    return binary_list

def bin_to_text(binary_list):
    chars = [''.join(binary_list[i:i+8]) for i in range(0, len(binary_list), 8)]
    text = ''.join([chr(int(b, 2)) for b in chars])

    return text

def img_pixels_to_bin(img):
    pixels = list(img.getdata())

    for i in range(len(pixels)):
        pixels[i] = list(pixels[i])
        for j in range(3):
            pixels[i][j] = bin(pixels[i][j])[2:].zfill(8)

    return pixels 

def burn_message(img_binary_pixels, binary_message):
    if len(binary_message) >= len(img_binary_pixels) * 3:
        raise ValueError("A mensagem é muito grande para essa imagem.")

    message_index = 0

    for i in range(len(img_binary_pixels)):
        for j in range(3):
            img_binary_pixels[i][j] = img_binary_pixels[i][j][:-1] + binary_message[message_index]
            message_index += 1
            
            if message_index >= len(binary_message):
                break

        if message_index >= len(binary_message):
            break

    return img_binary_pixels

def save_new_img(img_binary_pixels, size):
    decimal_pixels = []
    for pixel in img_binary_pixels:
        r = int(pixel[0], 2)   # Converte 8 bits para a cor vermelha
        g = int(pixel[1], 2)   # Converte 8 bits para a cor verde
        b = int(pixel[2], 2)   # Converte 8 bits para a cor azul
        decimal_pixels.append((r, g, b))  # Adiciona o pixel como uma tupla (R, G, B)
    
    new_image = Image.new("RGB", size)
    new_image.putdata(decimal_pixels)

    new_image.save(f"steg_{time.time() * 1000}.png")

def message_rendezvous(binary_pixels, message_lenght):
    extracted_bits = []

    for i in range(len(binary_pixels)):
        for j in range(3):
            extracted_bits.append(binary_pixels[i][j][-1])  # Último bit de cada canal

            if len(extracted_bits) >= message_lenght * 8:
                break

        if len(extracted_bits) >= message_lenght * 8:
            break

    extracted_message = ''.join(extracted_bits)
    true_message = bin_to_text(extracted_message)

    return true_message

def hide(img_path, text):
    img, img_size, pixels = open_image(img_path)
    binary_message = text_to_bin(text)
    bin_pixels = img_pixels_to_bin(img)
    new_bin_pixels = burn_message(bin_pixels, binary_message)
    save_new_img(new_bin_pixels, img_size)

    print(f"Tamanho da mensagem: {len(text)}")


def extract(img_path, message_lenght):
    img, img_size, pixels = open_image(img_path)
    bin_pixels = img_pixels_to_bin(img)
    message = message_rendezvous(bin_pixels, message_lenght)

    print(f"\nMensagem extraida: {message}")

def main():
    parser = argparse.ArgumentParser(
        prog="steganoPy.py",
        description="Tool de esteganografia utilizando LSB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplos de uso:\n"
               "  steganoPy.py -d -i imagem.png -m \"mensagem secreta\"\n"
               "  steganoPy.py -e -i imagem.png -l 16"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-d", "--hide", action="store_true", help="Esconder uma mensagem em uma imagem")
    group.add_argument("-e", "--extract", action="store_true", help="Extrair uma mensagem de uma imagem")

    parser.add_argument("-i", "--input", help="Caminho para a imagem de entrada", required=True)
    parser.add_argument("-m", "--mensagem", help="Mensagem a ser escondida (necessário com -s)")
    parser.add_argument("-l", "--tamanho", type=int, help="Tamanho da mensagem a ser recuperada (necessário com -e)")

    args = parser.parse_args()

    if args.hide:
        if not args.mensagem:
            parser.error("Para esconder uma mensagem, use -m junto com -d")
        hide(args.input, args.mensagem)
    
    elif args.extract:
        if args.tamanho is None:
            parser.error("Para extrair uma mensagem, use -l junto com -e")
        extract(args.input, args.tamanho)

if __name__ == "__main__":
    main()
