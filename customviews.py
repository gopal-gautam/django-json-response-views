from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import FieldFile
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.generic import CreateView
from django.views.generic import DeleteView


class DjangoJSONEncoderWithFileField(DjangoJSONEncoder):
    """
        DjangoJSONEncoder subclass that knows how to encode filefield.
    """
    def default(self, o):
        if isinstance(o, FieldFile):
            return o.url
        else:
            return super(DjangoJSONEncoderWithFileField, self).default(o)

class JSONModelResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, model, **response_kwargs):
        """
        Returns a JSON response, transforming 'model' to make the payload.
        """
        return JsonResponse(self.get_data(model=model), encoder=DjangoJSONEncoderWithFileField, **response_kwargs)

    def get_data(self, model):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return model_to_dict(model)


class UpdateOrCreateJsonResponseCreateView(JSONModelResponseMixin, CreateView):

    lookup_param = {}

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def _update_or_create(self, form):
        self.object, self.created = self.model.objects.update_or_create(defaults=form.cleaned_data, **self.lookup_param)
        if self.created:
            message = "New %s object with pk: %s is created" % (self.model.__name__, self.object.pk)
            print message  # TODO: Add logger here instead of this

    def form_valid(self, form):
        self._update_or_create(form)
        return self.render_to_json_response(self.object)


class JsonResponseDeleteView(JSONModelResponseMixin, DeleteView):

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        respond with the same object attributes as json
        """
        self.object = self.get_object()
        message = "%s object with pk: %s going to be deleted...." % (self.model.__name__, self.object.pk)
        self.object.delete()
        message += "delete done"
        print message #TODO: use logger here
        return self.render_to_json_response(self.object)
