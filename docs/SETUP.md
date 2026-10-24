# Setup guide

Work through these in order. Everything here stays within the AWS free tier.

## Step 0: Set up the account safely

1. Create an AWS account at https://aws.amazon.com/free.
2. **Before you create anything else:** Billing and Cost Management > Budgets > Create budget > "Monthly cost budget", set **$1.00**, and add alert thresholds at **50%, 80%, and 100%** sent to your email.
3. Turn on MFA for the root user (IAM > Security recommendations).
4. IAM > Users > Create user (for example `yourname-admin`), tick "Provide user access to the AWS Management Console", and attach the **AdministratorAccess** policy. Turn on MFA for this user as well.
5. Sign out of root and use the IAM user from now on. Make a note of the account sign-in URL.
6. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html), then run `aws configure` (or `aws configure sso`) as the IAM user.

## Step 1: Personalize the résumé

Edit `site/index.html`: replace `Your Name`, the contact links, the expected graduation date, and the skills. Open it in a browser to check it. The counter shows `…` until the API is connected.

## Steps 2 and 3: Deploy S3, CloudFront, DynamoDB, Lambda, and API Gateway

One template creates all of it:

```bash
cd infra
sam build
sam deploy --guided   # stack name: cloud-resume, region: us-east-1, accept the defaults
```

When it finishes, it prints these outputs: `SiteBucketName`, `DistributionId`, `SiteUrl`, and `ApiUrl`.

Do a first upload by hand to test it:

```bash
echo "window.VISITOR_API_URL = \"<ApiUrl>\";" > ../site/config.js
aws s3 sync ../site/ s3://<SiteBucketName> --delete
```

Open `SiteUrl`. CloudFront can take about 5 minutes to deploy. The page should load over HTTPS and the counter should go up each time you refresh. Opening the S3 object URL directly should return **Access Denied**, which shows the bucket is private.

## Step 4: CI/CD with GitHub Actions (OIDC, no stored keys)

1. IAM > Identity providers > Add provider > OpenID Connect
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
2. IAM > Roles > Create role > Web identity, then pick that provider, audience `sts.amazonaws.com`, GitHub organization `1011006014`, repository `my-first-webpage`, branch `main`.
3. Instead of a managed policy, add this inline policy (fill in your values):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": "arn:aws:s3:::<SiteBucketName>" },
    { "Effect": "Allow", "Action": ["s3:PutObject", "s3:DeleteObject"], "Resource": "arn:aws:s3:::<SiteBucketName>/*" },
    { "Effect": "Allow", "Action": "cloudfront:CreateInvalidation", "Resource": "arn:aws:cloudfront::<ACCOUNT_ID>:distribution/<DistributionId>" }
  ]
}
```

4. In the GitHub repo, go to Settings > Secrets and variables > Actions:
   - **Secret** `AWS_ROLE_ARN`: the role's ARN
   - **Variables** `SITE_BUCKET`, `DISTRIBUTION_ID`, `VISITOR_API_URL` (the `ApiUrl` output), and `AWS_REGION` (for example `us-east-1`)
5. Test it: change one word in `site/index.html`, push to `main`, watch the Actions tab, then refresh the live site.

## Step 5: Make it résumé-ready

- Replace `YOUR-CLOUDFRONT-DOMAIN` in `README.md` and `site/index.html` with your real CloudFront domain.
- Pin the repo: on your GitHub profile, click "Customize your pins" and select `my-first-webpage`.
- The Projects section of the résumé already links to the live site and the repo.

## Tearing it down

```bash
aws s3 rm s3://<SiteBucketName> --recursive
sam delete --stack-name cloud-resume
```
