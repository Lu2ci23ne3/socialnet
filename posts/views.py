from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Só o autor pode editar/apagar; qualquer um autenticado pode ler."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id


class PostListCreateView(generics.ListCreateAPIView):
    """Lista todos os posts (mais recentes primeiro) ou cria um novo post."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.select_related("author").prefetch_related("likes", "comments")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FeedView(generics.ListAPIView):
    """
    Feed personalizado: posts de quem o usuário segue + os próprios posts.
    Se o usuário ainda não segue ninguém, cai de volta para o feed geral.
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = list(user.following.values_list("id", flat=True))
        qs = Post.objects.select_related("author").prefetch_related("likes", "comments")
        if following_ids:
            qs = qs.filter(Q(author_id__in=following_ids) | Q(author=user))
        return qs


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    queryset = Post.objects.select_related("author").prefetch_related("likes", "comments")


class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"detail": "Post não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return Response({"liked": liked, "likes_count": post.likes_count})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["pk"]).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["pk"])

from django.shortcuts import render # se já não tiver lá em cima

def home(request):
    return render(request, 'posts/home.html')