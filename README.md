# New JsonResponseView mixins for Django

### DjangoJSONEncoderWithFileField
###### Implements Django json encoder with encoding file field adding url of the file to the json outpur

### JSONModelResponseMixin
###### A simple mixin that has ability to covert model to dict object and then respond the dict object encoding to json format

### UpdateOrCreateJsonResponseCreateView
###### This custom view can be used as Django model's update_or_create and also respond with created/updated model into json format

### JsonResponseDeleteView
###### Delete model object and respond same object in json encoded format

** Example: **
`Model`
```Python
class Application(models.Model):
    registration_date = models.CharField(max_length=15)
    reg = models.ForeignKey(NewRegistration)


class RegistrationDocument(models.Model):
    reg = models.ForeignKey(to=NewRegistration)
    remarks = models.TextField(null=True, blank=True)
    document_name = models.CharField(max_length=140, blank=True, null=True)
    _created_timestamp = models.DateTimeField(auto_now_add=True)
    _updated_timestamp = models.DateTimeField(auto_now=True)
    attached_file = models.FileField(upload_to="attached_files/")

    class Meta:
        abstract = True


class RequiredDocument(RegistrationDocument):
    attached_document = models.ForeignKey(to=system_settings.models.NewRegistrationRequiredDocument)
```

`Views`
```Python
class RegistrationDetailUpdateCreateView(UpdateOrCreateJsonResponseCreateView):
    """
    This is custom update or create view that inherits custom UpdateOrCreateJsonResponseCreateView. This CBV is
    used to create any object or update if provided lookup matches and returns the created object as json object
    if the form has reg field then the object is updated and if the form has id field which corresponds to the
    object id then also the object is update.
    """
    lookup_param = {}

    def form_valid(self, form):
        """
        The overriding is simply performed to access the form and reg and id parameter of it.
        :param form:
        :return:
        """
        if self.request.POST.get('id'):
            self.lookup_param['id'] = self.request.POST.get('id')
        elif form.cleaned_data.get('reg'):
            self.lookup_param['reg'] = form.cleaned_data.get("reg")
        else:
            raise Http404("No registration associated with this instance form")
        return super(RegistrationDetailUpdateCreateView, self).form_valid(form)


class ApplicationCreate(RegistrationDetailUpdateCreateView):
    model = models.Application
    fields = '__all__'
```

```Python
class RequiredDocumentDeleteView(JsonResponseDeleteView):
    model = models.RequiredDocument
```