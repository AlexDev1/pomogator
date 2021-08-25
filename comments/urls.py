from django.conf.urls import url

from tourprom.comments.views import ajax_expand_comments, ajax_post_comment, ajax_is_auth, change_comment_vote_view

urlpatterns =[
    # 'tourprom.comments.views',
    url(r'^ajax/expand_comments/(\w+)/(\d+)/$',
        ajax_expand_comments, name="ajax-expand-comments"),
    url(r'^ajax/post_comment/$',
        ajax_post_comment, name="ajax-post-comment"),
    url(r'^ajax/is_auth/$', ajax_is_auth, name="ajax-is-auth"),
    url(r'^comment_vote/$', change_comment_vote_view, name="comment-vote"),
]
