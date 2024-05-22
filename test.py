from PIL import Image, ImageDraw

def crop_to_circle(image_path, output_path):
    # 画像を開く
    img = Image.open(image_path).convert("RGBA")
    
    # サイズを取得
    width, height = img.size
    min_size = min(width, height)
    
    # 正方形にトリミング
    left = (width - min_size) // 2
    top = (height - min_size) // 2
    right = (width + min_size) // 2
    bottom = (height + min_size) // 2
    img = img.crop((left, top, right, bottom))
    
    # 円形のマスクを作成
    mask = Image.new("L", (min_size, min_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, min_size, min_size), fill=255)
    
    # マスクを適用
    result = Image.new("RGBA", (min_size, min_size))
    result.paste(img, (0, 0), mask)
    
    # 結果を保存
    result.save(output_path)

# 使用例
crop_to_circle("zundamonIcon.png", "output_image.png")