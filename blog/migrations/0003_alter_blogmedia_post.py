from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_blogpost_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogmedia',
            name='post',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='media',
                to='blog.blogpost',
            ),
        ),
    ]
