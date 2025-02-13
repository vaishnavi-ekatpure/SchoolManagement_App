from .models import *

def seeder():
    try:
        class_list = Class.objects.all()
        if class_list:
            class_list.delete()

        print('Delete all data')
        Class.objects.bulk_create([
            Class(class_name='First Standard'),
            Class(class_name='Second Standard'),
            Class(class_name='Third Standard'),
            Class(class_name='Fourth Standard'),
            Class(class_name='Fifth Standard'),
            Class(class_name='Sixth Standard'),
            Class(class_name='Seven Standard'),
            Class(class_name='Eight Standard'),
            Class(class_name='Nine Standard'),
            Class(class_name='Ten Standard'),
        ])

    except Exception as e:
        print(e)    