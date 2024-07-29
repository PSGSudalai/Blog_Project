from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from .models import Blogs,Tag,Comments,MailNotification,BlogView
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import BlogForm,CommentForm,TagForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache 
from django.urls import reverse


def regist_view(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another username.')
            
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email address is already in use. Please use another email.')

        elif password1 == password2:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=firstname,
                last_name=lastname
            )
            if 'mailing' in request.POST: 
                MailNotification.objects.create(email=email, subscribed=True) 

            login(request, user)
            messages.success(request, 'Registration successful')
            return redirect('home')
        else:
            messages.error(request, 'Passwords do not match. Please try again.')

    return render(request, 'apps/Register.html')
                
def Signin(request):
    if request.method == "POST":
        username = request.POST.get('username')  
        password = request.POST.get('password')  
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid UserName or Password")
            return redirect('Signin')

    return render(request, 'apps/Signin.html')

def Signout(request):
    logout(request)
    return redirect('home')

def index(request):

    searching = request.GET.get('search', '')  
    blogs= Blogs.objects.filter((Q(tags__blog_tags__icontains=searching )|
                                Q( blog_description__icontains=searching )
                                | Q(blog_title__icontains=searching ))).distinct()
    

    tags= Tag.objects.all()
    count = blogs.filter(status__icontains='Approved').count()    
    home_url = request.build_absolute_uri(reverse('home'))
    context = {'blogs': blogs, 'tags': tags, 'count': count, 'home_url': home_url}
    return render(request, 'apps/home.html', context)

def create_Blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            new_blog = form.save(commit=False)
            new_blog.host = request.user
            new_blog.status = 'Pending'
            new_blog.save()

            # Now save the many-to-many relationship
            form.save_m2m()
            messages.success(request, 'Blog Created successfully!')

            # Get the absolute URL for the blog post
            blog_url = request.build_absolute_uri(reverse('blog', args=[new_blog.pk]))

            if request.user.is_superuser:
                new_blog.status = 'Approved'
                new_blog.save()

                user_subject = f'New Blog: {new_blog.blog_title}'
                user_message = (
                    f"To Read the blog post '{new_blog.blog_title}'.\n\n"
                    f"Click this link: {blog_url}\n\n"
                    f"Thank you for using our platform!"
                )

                Subscribed_email = MailNotification.objects.filter(subscribed=True)
                subscribed_emails = [notification.email for notification in Subscribed_email]
                send_mail(user_subject, user_message, 'sudalaimuthu425@gmail.com', subscribed_emails)

            else:
                # Notify the admin
                subject = f'New Blog: {new_blog.blog_title}'
                message = (
                    f"New blog post: {new_blog.blog_title}\n\n"
                    f"Blog Description: {new_blog.blog_description}.\n\n"
                    f"From user {request.user}\n\nThe Email of the user is {request.user.email}"
                )

                superuser = User.objects.filter(is_superuser=True).first()
                if superuser:
                    recipient_list = [superuser.email]
                    send_mail(subject, message, 'sudalaimuthu425@gmail.com', recipient_list)
                else:
                    recipient_list = ['sudalaimuthu425@gmail.com']
                    send_mail(subject, message, 'sudalaimuthu425@gmail.com', recipient_list)

                # Notify the creator
                user_subject = f'Your Blog: {new_blog.blog_title} - Status Update'
                user_message = (
                    f"Your blog post '{new_blog.blog_title}' has been submitted for review."
                    f"We will update you on the status.\n\n"
                    f"Blog Description: {new_blog.blog_description}.\n\n"
                    f"Thank you for using our platform!"
                )

                user_email = request.user.email
                send_mail(user_subject, user_message, 'sudalaimuthu425@gmail.com', [user_email])

            return redirect('home')
        else:
            # Print form errors to console
            print(form.errors)
    else:
        form = BlogForm()
        
    context = {"form": form}
    return render(request, 'apps/newBlog.html', context)


def edit_Blog(request, pk):
    blog = get_object_or_404(Blogs, id=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog_title = form.cleaned_data['blog_title']
            blog_description = form.cleaned_data['blog_description']
            new_blog = form.save(commit=False)
            new_blog.host = request.user
            new_blog.status = 'Pending'

            if request.user.is_superuser:
                new_blog.status = 'Approved'
            
            new_blog.save()
            messages.success(request, 'Blog edited successfully!')

            # Notify the admin
            subject = f'New Blog: {blog_title}'
            message = (
                f"New blog post: {blog_title}\n\n"
                f"Blog Description: {blog_description}.\n\n"
                f"From user {request.user}\n\nThe Email of the user is {request.user.email}"
            )

            superuser = User.objects.filter(is_superuser=True).first()
            recipient_list = [superuser.email] if superuser else ['sudalaimuthu425@gmail.com']
            send_mail(subject, message, 'sudalaimuthu425@gmail.com', recipient_list)

            # Notify the user
            user_subject = f'Your Blog: {blog_title} - Status Update'
            user_message = (
                f"Your blog post '{blog_title}' has been submitted for review. "
                f"We will update you on the status.\n\n"
                f"Blog Description: {blog_description}.\n\n"
                f"Thank you for using our platform!"
            )

            send_mail(user_subject, user_message, '', [request.user.email])

            return redirect('home')
    else:
        form = BlogForm(instance=blog)

    context = {"form": form}
    return render(request, 'apps/newBlog.html', context)

def delete_Blog(request,pk):
    blog = Blogs.objects.get(id=pk)
    blog.delete()
    messages.success(request, 'Blog deleted successfully!')
    return redirect('home')




@login_required(login_url='Signin')
def blogs(request, pk):
    blog = Blogs.objects.get(id=pk)
    comments = Comments.objects.filter(blog=blog)

    view_count_key = f'blog_view_count_{pk}'
    view_count = cache.get(view_count_key, 0)

    if not request.session.get(f'visited_blog_{pk}', False):
        # If the user hasn't visited this blog during this session, increment the view count.
        view_count += 1
        # Mark this blog as visited by the user in their session.
        request.session[f'visited_blog_{pk}'] = True
        cache.set(view_count_key, view_count)

    if request.method == 'POST':
        ccc = request.POST['ccc']
        comment = Comments(blog=blog, text=ccc, host=request.user)
        comment.save()

    blog_url = request.build_absolute_uri(reverse('blog', args=[pk]))
    context = {'blogs': blog, 'comments': comments, 'blog_url': blog_url,'view_count':view_count}
    return render(request, 'apps/BlogPage.html', context)



def edit_Cmt(request,pk,pk1):
    comment=Comments.objects.get(id=pk)
    form = CommentForm(instance=comment)
    if request.method == 'POST':
        form = CommentForm(request.POST,instance=comment)
        if form.is_valid():
            form.instance.blog_id = pk1
            form.instance.host=request.user
            form.save()
            return redirect(f'/blog/{pk1}') 
    context = {"form": form}
    return render(request, 'apps/comments_form.html', context)


def delete_Cmt(request,pk,pk1):
    comment=Comments.objects.get(id=pk)
    comment.delete()
    return redirect(f'/blog/{pk1}')





def approve(request,pk):
    blog = Blogs.objects.get(id=pk)
    blog.status = 'Approved'
    # print(blog.status)
    user_subject = f'Your Blog: {blog.blog_title} - Status Update'
    user_message = (
        f"Your blog post '{blog.blog_title}' has been Approved. "
        f"Blog Description: {blog.blog_description}.\n\n"
        f"Blog Status: {blog.status}.\n\n"
        f"Thank you for using our platform!"
    )
    from_email=''
    user_email =blog.host.email
    send_mail(user_subject, user_message, from_email, [user_email])
    blog.save()
    messages.success(request, 'Blog approved successfully!')
    # Notify the all Subscribed user
    blog_url = request.build_absolute_uri(reverse('blog', args=[pk]))
    user_subject = f'New Blog: {blog.blog_title}'
    user_message = (
        f"To Read the  blog post '{blog.blog_title}' . \n\n "
        f"Click this link :   {blog_url}  .\n\n"
    )

    Subscribed_email = MailNotification.objects.filter(subscribed=True)
    subscribed_emails = [notification.email for notification in Subscribed_email]
    send_mail(user_subject, user_message, from_email, subscribed_emails)
    return redirect('home')


def reject(request,pk):
    blog = Blogs.objects.get(id=pk)
    blog.status = 'Rejected'
    
    user_subject = f'Your Blog: {blog.blog_title} - Status Update'
    user_message = (
        f"Your blog post '{blog.blog_title}' has been Rejected. "
        f"Blog Description: {blog.blog_description}.\n\n"
        f"Blog Status: {blog.status}.\n\n"
        f"Thank you for using our platform!"
    )
    from_email=''
    user_email =blog.host.email
    send_mail(user_subject, user_message, from_email, [user_email])
    blog.delete()
    messages.error(request, 'Blog rejected!')
    return redirect('home')


def create_tag(request):
    form = TagForm()
    if request.method == 'POST':
        form= TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
        
    context = {"form": form}
    return render(request, 'apps/newTag.html', context)

def profile(request):
    comment=Comments.objects.all()
    blogs =Blogs.objects.filter(host=request.user)
    count = blogs.filter().count()  
    approved_count = blogs.filter(status ='Approved').count() 
    pending_count =blogs.filter(status ='Pending').count()   
    rejected_count = blogs.filter(status ='Rejected').count()  
    # count=approved_count+pending_count+rejected_count  
    context={'comment':comment,'blogs':blogs,'count':count, 'approved_count':approved_count, 'rejected_count':rejected_count,'pending_count':pending_count}
    return render(request,'apps/profile.html',context)
