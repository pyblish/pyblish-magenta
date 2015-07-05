import pyblish.api


@pyblish.api.log
class CollectInstanceData(pyblish.api.Collector):
    """Inject all instances with the Context's asset data.


    This transfers data from the Context to each Instance.
    """
    order = pyblish.api.Collector.order + 0.49

    def process(self, context, instance):

        for key in ['root', 'asset', 'container', 'workFile']:

            value = context.data(key, None)
            if value is not None:
                instance.set_data(key, value)
            else:
                self.log.debug("Context does not have data '{0}'".format(key))