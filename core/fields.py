from django.db.models.fields import CharField


class YoutubeVideoLinkField(CharField):
    # default_validators = [validators.validate_email]
    description = "Ссылка на youtube-видео"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 600)
        CharField.__init__(self, *args, **kwargs)

    def formfield(self, **kwargs):
        # As with CharField, this will cause email validation to be performed
        # twice.
        defaults = {
            # 'form_class': forms.EmailField,
        }
        defaults.update(kwargs)
        return super(YoutubeVideoLinkField, self).formfield(**defaults)

    def get_video_id(self):
        from urllib.parse import urlparse, parse_qs
        from re import match

        # Просто выдёргиваем из URL GET, а из GET значение 'v'
        adr = urlparse(self.link)
        qs = parse_qs(adr.query)

        if match('.*youtu\.be', adr.netloc):
            vid = adr.path.split('/')[1]
        else:
            try:
                vid = qs['v'][0]
            except KeyError:
                vid = ''

        return vid

    def thumb(self):
        vid = self.youtube_video_id()
        return 'http://img.youtube.com/vi/%s/mqdefault.jpg' % vid

    def embed(self):
        vid = self.video_id()
        return '//www.youtube.com/embed/' + vid


class YoutubeVideoLinkMixin(object):
    video_link_field_name = 'video_link'

    def get_youtube_video_id(self):
        from urllib.parse import urlparse, parse_qs
        from re import match

        # Просто выдёргиваем из URL GET, а из GET значение 'v'
        adr = urlparse(getattr(self, self.video_link_field_name))
        qs = parse_qs(adr.query)

        if match('.*youtu\.be', adr.netloc):
            vid = adr.path.split('/')[1]
        else:
            try:
                vid = qs['v'][0]
            except KeyError:
                vid = ''

        return vid

    def get_youtube_thumb(self):
        vid = self.get_youtube_video_id()
        return 'http://img.youtube.com/vi/%s/mqdefault.jpg' % vid

    def get_youtube_embed(self):
        vid = self.get_youtube_video_id()
        return '//www.youtube.com/embed/' + vid
