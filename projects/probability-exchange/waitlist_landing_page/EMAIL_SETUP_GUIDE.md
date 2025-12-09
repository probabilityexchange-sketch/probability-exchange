# Probex Waitlist Email Setup Guide

## 🎯 Custom Email Notifications Configuration

### Step 1: Update Your Email Address

Edit `netlify.toml` and replace `your-email@example.com` with your actual email:

```toml
[forms.waitlist]
  to = "your-actual-email@domain.com"  # ← UPDATE THIS
```

### Step 2: Deploy to Netlify

1. Commit and push your changes:
   ```bash
   git add .
   git commit -m "Add custom email template and form configuration"
   git push origin main
   ```

2. Deploy to Netlify (if not already done)

### Step 3: Configure Netlify Forms

1. **Go to Netlify Dashboard** → Your Site → **Forms**
2. **Click "Settings"** next to your waitlist form
3. **Configure notification settings**:
   - ✅ Email notifications: Enabled
   - ✅ From: `noreply@your-site.netlify.app`
   - ✅ To: Your email address
   - ✅ Subject: `🎉 New Probex Waitlist Signup!`

### Step 4: Test Your Form

1. **Visit your live site**
2. **Enter a test email**
3. **Check your inbox** (should receive custom HTML email)

## 📧 Email Template Features

Your custom email includes:
- ✅ **Professional branding** with Probex colors
- ✅ **Submission statistics** (total signups, today's count)
- ✅ **Complete user data** (email, IP, user agent, referrer)
- ✅ **Actionable next steps** for each signup
- ✅ **Responsive design** for mobile/desktop

## 🔧 Advanced Configuration

### Multiple Recipients:
```toml
[forms.waitlist]
  to = ["admin@probex.com", "team@probex.com"]
```

### Conditional Notifications:
```toml
[forms.waitlist]
  to = "admin@probex.com"
  cc = "team@probex.com"
  bcc = "analytics@probex.com"
```

### Custom Subject Lines:
```toml
subject = "🚀 Probex Waitlist: {{ email }} just joined! ({{ submission_count }} total)"
```

## 📊 Available Template Variables

Your email template can use these variables:
- `{{ email }}` - User's email address
- `{{ timestamp }}` - Submission time
- `{{ date }}` - Current date
- `{{ ip }}` - User's IP address
- `{{ user_agent }}` - Browser information
- `{{ referrer }}` - Page they came from
- `{{ submission_count }}` - Total form submissions
- `{{ today_count }}` - Today's submissions

## 🛡️ Spam Prevention

Netlify automatically includes:
- ✅ **Honeypot fields** (hidden from users)
- ✅ **Rate limiting** (prevents abuse)
- ✅ **Akismet integration** (optional)
- ✅ **reCAPTCHA** (optional, free tier available)

## 📈 Analytics & Export

### View Submissions:
1. **Netlify Dashboard** → Forms → Submissions
2. **Filter by date** or search by email
3. **Export as CSV** for email marketing tools

### Integration Options:
- **Mailchimp**: Import CSV manually or via API
- **ConvertKit**: Use webhook integration
- **SendGrid**: Connect via Netlify Functions
- **Custom**: Build webhook to your email service

## 🚀 Next Steps

1. **Test the form** with multiple email addresses
2. **Set up email marketing** (Mailchimp, ConvertKit, etc.)
3. **Create welcome email sequence** for new subscribers
4. **Monitor conversion rates** and optimize landing page

## 🔍 Troubleshooting

### Emails Not Arriving:
- Check spam folder
- Verify email address in `netlify.toml`
- Check Netlify Forms dashboard for errors

### Form Not Submitting:
- Ensure site is deployed to Netlify
- Check browser console for JavaScript errors
- Verify form has proper HTML structure

### Template Not Working:
- Ensure `netlify-email-template.html` is in root directory
- Check template syntax for errors
- Verify Netlify is using latest configuration

---

**Need help?** Check Netlify's [Forms documentation](https://docs.netlify.com/forms/setup/) or contact support.