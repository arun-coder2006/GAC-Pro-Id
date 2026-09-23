from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image as PILImage
from io import BytesIO
import os


# ============================================================
# SETTINGS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4


# ============================================================
# FIT TEXT INTO AVAILABLE WIDTH
# ============================================================

def draw_fitted_text(
    c,
    text,
    x,
    y,
    max_width,
    font="Times-Bold",
    font_size=8
):

    text = str(text)

    size = font_size

    while size > 5:

        text_width = stringWidth(
            text,
            font,
            size
        )

        if text_width <= max_width:
            break

        size -= 0.25

    c.setFont(
        font,
        size
    )

    c.drawString(
        x,
        y,
        text
    )


# ============================================================
# DRAW PHOTO
# ============================================================

def draw_photo(
    c,
    photo_path,
    x,
    y,
    width,
    height
):

    # --------------------------------------------------------
    # PHOTO BORDER
    # --------------------------------------------------------

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.8)

    c.rect(
        x,
        y,
        width,
        height,
        fill=0,
        stroke=1
    )

    # --------------------------------------------------------
    # CHECK PHOTO
    # --------------------------------------------------------

    if not photo_path:
        return

    if not os.path.isfile(photo_path):

        print(
            "PHOTO NOT FOUND:",
            photo_path
        )

        return

    try:

        image = PILImage.open(
            photo_path
        )

        image_width, image_height = image.size

        scale = min(
            width / image_width,
            height / image_height
        )

        final_width = (
            image_width * scale
        )

        final_height = (
            image_height * scale
        )

        final_x = (
            x +
            (width - final_width) / 2
        )

        final_y = (
            y +
            (height - final_height) / 2
        )

        c.drawImage(
            ImageReader(photo_path),
            final_x,
            final_y,
            width=final_width,
            height=final_height,
            preserveAspectRatio=True,
            mask="auto"
        )

        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.8)

        c.rect(
            x,
            y,
            width,
            height,
            fill=0,
            stroke=1
        )

    except Exception as e:

        print(
            "PHOTO ERROR:",
            photo_path
        )

        print(e)


# ============================================================
# DRAW ONE COMPLETE ID CARD
# ============================================================

def draw_id_card(
    c,
    student,
    card_y
):

    # ========================================================
    # CARD SIZE
    # ========================================================

    card_x = 75

    card_width = 462

    card_height = 205

    card_top = card_y + card_height


    # ========================================================
    # OUTER BORDER
    # ========================================================

    c.setStrokeColorRGB(0, 0, 0)

    c.setLineWidth(0.9)

    c.rect(
        card_x,
        card_y,
        card_width,
        card_height,
        fill=0,
        stroke=1
    )


    # ========================================================
    # HEADER
    # ========================================================

    c.setFillColorRGB(0, 0, 0)

    c.setFont(
        "Times-Bold",
        8.5
    )

    c.drawCentredString(
        PAGE_WIDTH / 2,
        card_top - 14,
        "GOVERNMENT ARTS COLLEGE (AUTONOMOUS)"
    )

    c.drawCentredString(
        PAGE_WIDTH / 2,
        card_top - 25,
        "COIMBATORE - 641 018"
    )

    c.drawCentredString(
        PAGE_WIDTH / 2,
        card_top - 36,
        "PROVISIONAL IDENTITY CARD"
    )


    # ========================================================
    # FIELD POSITIONS
    # ========================================================

    label_x = card_x + 20

    colon_x = card_x + 155

    value_x = card_x + 168

    name_y = card_top - 58

    roll_y = card_top - 78

    class_y = card_top - 98

    tutor_y = card_top - 119

    hod_y = card_top - 148


    # ========================================================
    # NAME
    # ========================================================

    c.setFont(
        "Times-Bold",
        7.5
    )

    c.drawString(
        label_x,
        name_y,
        "NAME"
    )

    c.drawString(
        colon_x,
        name_y,
        ":"
    )

    draw_fitted_text(
        c,
        student["name"],
        value_x,
        name_y,
        205,
        "Times-Bold",
        8
    )


    # ========================================================
    # ROLL NO
    # ========================================================

    c.drawString(
        label_x,
        roll_y,
        "ROLL NO"
    )

    c.drawString(
        colon_x,
        roll_y,
        ":"
    )

    draw_fitted_text(
        c,
        student["roll_no"],
        value_x,
        roll_y,
        205,
        "Times-Bold",
        8
    )


    # ========================================================
    # CLASS
    # ========================================================

    c.drawString(
        label_x,
        class_y,
        "CLASS"
    )

    c.drawString(
        colon_x,
        class_y,
        ":"
    )

    draw_fitted_text(
        c,
        student["class_name"],
        value_x,
        class_y,
        190,
        "Times-Bold",
        8
    )


    # ========================================================
    # PHOTO
    # ========================================================

    photo_width = 48

    photo_height = 60

    photo_x = (
        card_x +
        card_width -
        photo_width -
        30
    )

    photo_y = card_top - 112

    draw_photo(
        c,
        student.get("photo"),
        photo_x,
        photo_y,
        photo_width,
        photo_height
    )


    # ========================================================
    # CLASS TUTOR SIGNATURE
    # ========================================================

    c.drawString(
        label_x,
        tutor_y,
        "CLASS TUTOR'S SIGN."
    )

    c.drawString(
        colon_x,
        tutor_y,
        ":"
    )


    # ========================================================
    # HOD SIGNATURE
    # ========================================================

    c.drawString(
        label_x,
        hod_y,
        "HOD'S SIGNATURE"
    )

    c.drawString(
        colon_x,
        hod_y,
        ":"
    )


    # ========================================================
    # BOTTOM FROM / TO SECTION
    # ========================================================

    bottom_height = 25

    bottom_y = card_y


    c.line(
        card_x,
        bottom_y + bottom_height,
        card_x + card_width,
        bottom_y + bottom_height
    )


    # ========================================================
    # BOTTOM COLUMN WIDTHS
    # ========================================================

    from_width = 55

    college_width = 215

    to_width = 45

    x1 = (
        card_x +
        from_width
    )

    x2 = (
        x1 +
        college_width
    )

    x3 = (
        x2 +
        to_width
    )


    # ========================================================
    # VERTICAL LINES
    # ========================================================

    c.line(
        x1,
        bottom_y,
        x1,
        bottom_y + bottom_height
    )

    c.line(
        x2,
        bottom_y,
        x2,
        bottom_y + bottom_height
    )

    c.line(
        x3,
        bottom_y,
        x3,
        bottom_y + bottom_height
    )


    # ========================================================
    # FROM
    # ========================================================

    c.setFont(
        "Times-Bold",
        7
    )

    c.drawString(
        card_x + 5,
        bottom_y + 8,
        "FROM :"
    )


    # ========================================================
    # COLLEGE NAME
    # ========================================================

    draw_fitted_text(
        c,
        "GOVT ARTS COLLEGE COIMBATORE",
        x1 + 5,
        bottom_y + 8,
        college_width - 10,
        "Times-Bold",
        7
    )


    # ========================================================
    # TO
    # ========================================================

    c.setFont(
        "Times-Bold",
        7
    )

    c.drawString(
        x2 + 7,
        bottom_y + 8,
        "TO:"
    )


    # ========================================================
    # DESTINATION
    # ========================================================

    draw_fitted_text(
        c,
        student["to_place"],
        x3 + 5,
        bottom_y + 8,
        card_x + card_width - x3 - 10,
        "Times-Bold",
        7
    )


# ============================================================
# GENERATE PDF
# ============================================================

def generate_pdf(students):

    output = BytesIO()

    c = canvas.Canvas(
        output,
        pagesize=A4
    )


    # ========================================================
    # EXACT POSITIONS FROM YOUR ORIGINAL CODE
    # ========================================================

    card_positions = [
        580,
        318,
        57
    ]


    # ========================================================
    # PROCESS 3 STUDENTS PER PAGE
    # ========================================================

    for page_start in range(
        0,
        len(students),
        3
    ):

        page_students = students[
            page_start:
            page_start + 3
        ]


        for index, student in enumerate(
            page_students
        ):

            draw_id_card(
                c,
                student,
                card_positions[index]
            )


        c.showPage()


    # ========================================================
    # SAVE TO MEMORY
    # ========================================================

    c.save()

    output.seek(0)

    return output