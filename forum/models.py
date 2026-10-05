from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    department = models.CharField(max_length=100, blank=True)
    course = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=20, blank=True)
    skills = models.CharField(max_length=255, blank=True)
    interests = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    reputation = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    following_users = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    followed_topics = models.CharField(max_length=500, blank=True, help_text="Comma separated topics")

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Post(models.Model):
    POST_TYPES = (
        ('QUESTION', 'Question'),
        ('DISCUSSION', 'Discussion'),
        ('POLL', 'Poll'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('RESOURCE', 'Resource'),
        ('STUDY_SESSION', 'Study Session'),
        ('PROJECT_DISCUSSION', 'Project Discussion'),
    )
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='QUESTION', db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="posts")
    upvotes = models.ManyToManyField(User, related_name="upvoted_posts", blank=True)
    downvotes = models.ManyToManyField(User, related_name="downvoted_posts", blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags", db_index=True)
    is_solved = models.BooleanField(default=False, db_index=True)
    ai_quality_score = models.IntegerField(null=True, blank=True)
    ai_flags = models.CharField(max_length=255, blank=True)
    is_draft = models.BooleanField(default=False, db_index=True)
    views = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    @property
    def score(self):
        return self.upvotes.count() - self.downvotes.count()

class Comment(models.Model):
    comment_text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    is_accepted = models.BooleanField(default=False, db_index=True)
    upvotes = models.ManyToManyField(User, related_name="upvoted_comments", blank=True)
    downvotes = models.ManyToManyField(User, related_name="downvoted_comments", blank=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    @property
    def score(self):
        return self.upvotes.count() - self.downvotes.count()

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    created_date = models.DateTimeField(auto_now_add=True)
    moderators = models.ManyToManyField(User, related_name="moderated_communities")
    followers = models.ManyToManyField(User, related_name="followed_communities", blank=True)
    rules = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Communities"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Poll(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="poll")
    question = models.CharField(max_length=255)
    
    def __str__(self):
        return self.question

class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=255)

    def __str__(self):
        return self.choice_text

class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(PollChoice, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('poll', 'user')
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255, help_text="Link or physical location")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="attending_events", blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return self.title

class StudyGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_study_groups")
    members = models.ManyToManyField(User, related_name="study_groups", blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('PDF', 'PDF'),
        ('ARTICLE', 'Article'),
        ('VIDEO', 'Video'),
        ('REPO', 'Repository'),
        ('NOTES', 'Notes'),
        ('COURSE', 'Course'),
        ('WEBSITE', 'Website'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="resources")
    tags = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_resources")
    url = models.URLField()
    rating = models.IntegerField(default=0)
    upvotes = models.ManyToManyField(User, related_name="upvoted_resources", blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class StudentLearningGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_goals")
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0) # 0-100
    is_completed = models.BooleanField(default=False, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class StudentSkillSignal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skill_signals")
    topic = models.CharField(max_length=100, db_index=True)
    score = models.IntegerField(default=0) # Arbitrary points based on activity
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'topic')
        
    def __str__(self):
        return f"{self.user.username} - {self.topic}"

class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="practice_sessions")
    topic = models.CharField(max_length=100, db_index=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} Practice"

class UserBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking_users")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by_users")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} blocks {self.blocked.username}"

class ContentReport(models.Model):
    REPORT_TYPES = (
        ('SPAM', 'Spam'),
        ('HARASSMENT', 'Harassment'),
        ('MISINFO', 'Misinformation'),
        ('COPYRIGHT', 'Copyright concern'),
        ('UNSAFE', 'Unsafe content'),
        ('IMPERSONATION', 'Impersonation'),
        ('DUPLICATE', 'Duplicate'),
        ('OUTDATED', 'Outdated information'),
        ('OTHER', 'Other'),
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_reports")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    details = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.username} - {self.report_type}"

class ModerationAction(models.Model):
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mod_actions")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    action_type = models.CharField(max_length=50) # e.g., 'HIDDEN', 'LOCKED', 'WARNED'
    reason = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} by {self.moderator.username}"

class PostRevision(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="revisions")
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revision of {self.post.title} at {self.created_date}"

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    technology = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    members = models.ManyToManyField(User, related_name="collaborative_projects", blank=True)
    status = models.CharField(max_length=20, choices=(('PLANNING', 'Planning'), ('ACTIVE', 'Active'), ('REVIEW', 'Review'), ('COMPLETED', 'Completed')), default='PLANNING')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProjectTask(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    column = models.CharField(max_length=20, choices=(('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('REVIEW', 'Review'), ('DONE', 'Done')), default='TODO')
    due_date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class StudySessionEvent(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name="sessions")
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_sessions")
    start_time = models.DateTimeField()
    meeting_link = models.URLField(blank=True)
    participants = models.ManyToManyField(User, related_name="attending_sessions", blank=True)

    def __str__(self):
        return f"{self.title} - {self.group.name}"

# ==========================================
# PHASE 7: CAREERS & GAMIFICATION
# ==========================================
class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=50, choices=(
        ('FULL_TIME', 'Full Time'),
        ('INTERNSHIP', 'Internship'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract')
    ), default='FULL_TIME')
    description = models.TextField()
    apply_link = models.URLField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

class InterviewExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interview_experiences")
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    content = models.TextField()
    difficulty = models.IntegerField(default=3, choices=((1, 'Very Easy'), (2, 'Easy'), (3, 'Medium'), (4, 'Hard'), (5, 'Very Hard')))
    offer_status = models.CharField(max_length=20, choices=(
        ('ACCEPTED', 'Offer Accepted'),
        ('REJECTED', 'Offer Rejected'),
        ('PENDING', 'Pending'),
        ('NO_OFFER', 'No Offer')
    ), default='PENDING')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s experience at {self.company}"
