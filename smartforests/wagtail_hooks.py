from wagtail.core import hooks


@hooks.register('construct_page_action_menu')
def customise_page_actions(menu_items, request, context):
    '''
    Disallow non-admins from deleting pages
    '''
    if not request.user.is_superuser:
        try:
            for (index, item) in enumerate(menu_items):
                if item.name == 'action-delete':
                    menu_items.pop(index)
                    break
        except:
            pass

    '''
    Make 'publish' the default action in the editor UI.
    '''
    try:
        for (index, item) in enumerate(menu_items):
            if item.name == 'action-publish' or item.name == 'action-submit':
                menu_items.pop(index)
                menu_items.insert(0, item)
                break
    except:
        pass
