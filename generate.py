import io

import cairocffi as cairo
import cairosvg
import pangocairocffi as pangocairo
import pangocffi as pango
import pyqrcode
from PIL import Image


def bounded_layout(layout, font_desc, text, width, height, start_font=64):
    layout.text = text
    font_size = start_font
    while True:
        font_desc.size = pango.units_from_double(font_size)
        layout.font_description = font_desc
        _width, _height = (
            layout.get_extents()[1].width,
            layout.get_extents()[1].height,
        )
        if _width < pango.units_from_double(
            width
        ) and _height < pango.units_from_double(height):
            return pango.units_to_double(_width), pango.units_to_double(_height)
        font_size -= 1


def write_badge_text(
    context, x_offset, primary_name, secondary_name, line_1, line_2, pronouns
):
    context.save()
    context.set_line_width(1)
    context.set_source_rgb(0, 0, 0)

    layout = pangocairo.create_layout(context)

    layout.width = pango.units_from_double(234)
    layout.alignment = pango.Alignment.CENTER

    font_desc = pango.FontDescription()
    font_desc.family = "Kulim Park"
    font_desc.weight = 700
    font_desc.stretch = pango.Stretch.NORMAL
    font_desc.variant = pango.Variant.NORMAL

    _width, _height = bounded_layout(
        layout, font_desc, primary_name, 234, 100, start_font=70
    )
    context.move_to(x_offset, 200 - _height)
    pangocairo.show_layout(context, layout)

    font_desc.weight = 300
    _width, _height = bounded_layout(
        layout, font_desc, secondary_name, 234, 40, start_font=40
    )
    context.move_to(x_offset, 200)
    pangocairo.show_layout(context, layout)

    font_desc.weight = 400
    _width, _height = bounded_layout(layout, font_desc, line_1, 234, 30, start_font=21)
    context.move_to(x_offset, 285 - _height)
    pangocairo.show_layout(context, layout)

    font_desc.weight = 600
    _width, _height = bounded_layout(layout, font_desc, line_2, 234, 30, start_font=16)
    context.move_to(x_offset, 290)
    pangocairo.show_layout(context, layout)

    font_desc.weight = 600
    layout.width = pango.units_from_double(72)
    _width, _height = bounded_layout(layout, font_desc, pronouns, 72, 30, start_font=18)
    context.move_to(x_offset + 160, 120 - _height)
    pangocairo.show_layout(context, layout)

    context.restore()


def generate_badge_svg(
    attendee_code, primary_name, secondary_name, line_1, line_2, pronouns
):
    badge_template = cairosvg.surface.SVGSurface(
        cairosvg.parser.Tree(file_obj=open("badge-template.svg", "rb")), None, 72
    ).cairo

    qrcode = pyqrcode.create(attendee_code)
    buffer = io.BytesIO()
    qrcode.svg(buffer, scale=2)
    buffer.seek(0)
    qr_code = cairosvg.surface.SVGSurface(
        cairosvg.parser.Tree(file_obj=buffer), None, 72
    ).cairo

    badge = cairo.SVGSurface("output.svg", 306, 418)
    context = cairo.Context(badge)

    context.save()
    context.set_source_surface(badge_template, 0, 0)
    context.paint()
    context.set_source_surface(qr_code, 220, 8)
    context.paint()
    context.restore()

    write_badge_text(
        context, 36, primary_name, secondary_name, line_1, line_2, pronouns
    )


def generate_badge_pdf(
    attendee_code, primary_name, secondary_name, line_1, line_2, pronouns
):
    with open("badge-template.png", "rb") as badge_template_handler:
        badge_template_io = io.BytesIO(badge_template_handler.read())
        badge_template_image = Image.open(badge_template_io)
        imagebuffer = io.BytesIO()
        badge_template_image.save(imagebuffer, format="PNG")
        imagebuffer.seek(0)
        badge_template = cairo.ImageSurface.create_from_png(imagebuffer)

    qrcode = pyqrcode.create(attendee_code)
    buffer = io.BytesIO()
    qrcode.png(buffer, scale=8)
    buffer.seek(0)
    qr_im = Image.open(buffer)
    imagebuffer = io.BytesIO()
    qr_im.save(imagebuffer, format="PNG")
    imagebuffer.seek(0)
    qr_img = cairo.ImageSurface.create_from_png(imagebuffer)

    sheet = cairo.PDFSurface("output.pdf", 612, 792)
    context = cairo.Context(sheet)

    context.save()

    context.scale(0.24, 0.24)
    context.set_source_surface(badge_template, 0, 0)
    context.paint()
    context.set_source_surface(badge_template, 1275, 0)
    context.paint()

    context.scale(1, 1)
    context.set_source_surface(qr_img, 920, 45)
    context.paint()
    context.set_source_surface(qr_img, 2175, 45)
    context.paint()

    context.restore()

    context.save()

    context.set_line_width(1)
    context.set_dash([5, 5], 1)
    context.move_to(306, 0)
    context.line_to(306, 800)

    context.move_to(0, 417)
    context.line_to(712, 417)
    context.stroke()

    context.restore()

    write_badge_text(
        context, 36, primary_name, secondary_name, line_1, line_2, pronouns
    )
    write_badge_text(
        context, 342, primary_name, secondary_name, line_1, line_2, pronouns
    )

    sheet.show_page()


generate_badge_svg(
    "oTWhTX8HD5AEyh4x",
    "Ee",
    "Durbin",
    "Director of Infrastructure",
    "Python Software Foundation",
    "they/them",
)
generate_badge_pdf(
    "oTWhTX8HD5AEyh4x",
    "Ee",
    "Durbin",
    "Director of Infrastructure",
    "Python Software Foundation",
    "they/them",
)
