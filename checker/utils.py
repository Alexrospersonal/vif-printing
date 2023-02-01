import os
from io import BytesIO

from PIL import Image
from django.core.files import File

from checker.models import ItemCover, ItemPaper, Manager, Designer


def create_choices(qs_object):
    """
    function take query set and
    create choices [(pk, name), (pk, name), ....] for
    forms.ChoiceField
    """
    choices_list = []
    for obj in qs_object:
        choices_list.append((obj.pk, obj.__str__()))
    return choices_list


def compresing_image(image):
    original_img = Image.open(image)
    copy_of_image = original_img.copy()
    copy_of_image.thumbnail(size=(512, 512), resample=Image.Resampling.LANCZOS)
    img_io = BytesIO()
    copy_of_image.save(img_io, format='JPEG', quality=50)
    filename, ext = os.path.splitext(image.name)
    new_name = filename + "_thumbnail.jpeg"
    new_img = File(img_io, name=new_name)
    return new_img


def rename_image(image, product_name, front=False):
    name, ext = os.path.splitext(image.name)
    new_product_name = product_name.replace(' ', '_')
    if front:
        new_name = f'{new_product_name}_лице{ext}'
    else:
        new_name = f'{new_product_name}_зворот{ext}'
    image.name = new_name
    return image


def add_values_to_fields(obj, form, kwargs, request):
    obj_sizes_qs = obj.itemsize_set.all()
    obj_cover_qs = ItemCover.objects.filter(items__id=kwargs['pk']) & ItemCover.objects.filter(in_stock=True)
    obj_paper_qs = ItemPaper.objects.filter(items__id=kwargs['pk']) & ItemPaper.objects.filter(in_stock=True)
    manager = Manager.objects.all()
    designer = Designer.objects.all()
    form.fields['item'].choices = [(obj.pk, obj.__str__())]
    form.fields['size'].choices = create_choices(obj_sizes_qs)
    form.fields['cover'].choices = create_choices(obj_cover_qs)
    form.fields['paper'].choices = create_choices(obj_paper_qs)
    if hasattr(request.user.employee, 'manager'):
        form.fields['designer'].choices = create_choices(designer)
    elif hasattr(request.user.employee, 'designer'):
        form.fields['manager'].choices = create_choices(manager)
    return form


def get_image_size(image):
    return round(image.width * 25.4 / 300), round(image.height * 25.4 / 300)


def get_image_dpi( img, form_size):
    return round(((img.width * 25.4 / form_size[0]) + (img.height * 25.4 / form_size[1])) / 2)