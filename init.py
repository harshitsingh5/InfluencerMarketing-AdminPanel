from flask import Flask,render_template,url_for,jsonify,request,Response,session,redirect,flash
from models import *
from functools import wraps
from flask_migrate import Migrate
from threading import Thread

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:xyz2525xyz2525@localhost/mydb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
db.app=app
migrate = Migrate(app, db)


status={
    0:"Pending",
    1:"Active",
    2:"Completed"
}


def admin_login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		try:
			if session["logged_in"] and session["username"]=="admin":
				return f(*args, **kwargs)
			else:
				return redirect("/admin-login-page")
		except:
			return redirect("/admin-login-page")
	return wrap

def send_active_msg(camp_id):
    c=Campaign.query.filter_by(campaign_id=camp_id).first()
    if c.platform==0:
        inf_all=Influencer_details.query.filter_by(use_facebook=1).all()
    elif c.platform==1:
        inf_all=Influencer_details.query.filter_by(use_instagram=1).all()
    elif c.platform==2:
        inf_all=Influencer_details.query.filter_by(use_twitter=1).all()
    elif c.platform==3:
        inf_all=Influencer_details.query.filter_by(use_youtube=1).all()
    # if c.subtype==7 or c.subtype==8:
    #     for inf in inf_all:
    #         if inf.location[0] in c.location:
    #             send_push_notif(inf,"Congratulations! You are eligible for"+ str(c.name) +"campaign")
    # else:
    for inf in inf_all:
        send_push_notif(inf,"Congratulations! You are eligible for"+ str(c.name) +"campaign")


def send_complete_msg(camp_id):
    c=Campaign.query.filter_by(campaign_id=camp_id).first()
    all_inv=c.influencers
    for inf in all_inv:
        send_push_notif(inf,"Lets have a look at your performance in the"+ str(c.name) +"campaign")

@app.route("/admin")
def admin_Home():
	try:
		if session["logged_in"]:
			return redirect("/admin-dashboard")
		else:
			return redirect("/admin-login-page")
	except:
		return redirect("/admin-login-page")

@app.route("/admin-login-page",methods=["GET","POST"])
def admin_login_page():
    return render_template("login.html")

@app.route("/admin-login",methods=["GET","POST"])
def admin_login():
    #if request.form=="POST":
        username=request.form['username']
        password=request.form['password']
        if username=="admin" and password=="gz2019.inf.brand.&ult1m@te$h@rkw3@r3b3$t":
            session['logged_in']=True
            session['username']="admin"
            return redirect("/admin-dashboard")
        else:
            flash("Wrong Credentials")
            return render_template("login.html")
    # else:
    #     flash("Method Not Allowed")
    #     return render_template("login.html")

@app.route("/admin-active-campaign",methods=["GET","POST"])
@admin_login_required
def admin_active_campaign():
    try:
        cc=Campaign.query.filter_by(status=1).all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Active Campaigns",sts=1)
    except:
        return render_template("error.html")

@app.route("/admin-pending-campaign",methods=["GET","POST"])
@admin_login_required
def admin_pending_campaign():
    try:
        cc=Campaign.query.filter_by(status=0).all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Pending Campaigns",sts=0)
    except:
        return render_template("error.html")

@app.route("/admin-completed-campaign",methods=["GET","POST"])
@admin_login_required
def admin_completed_campaign():
    try:
        cc=Campaign.query.filter_by(status=2).all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,value="Completed Campaigns",sts=2)
    except:
        return render_template("error.html")




@app.route("/admin-logout",methods=["GET","POST"])
@admin_login_required
def admin_logout():
	try:
		mobile=session['username']
		session.pop('username',None)
		session['logged_in']=False
		# flash("Successfully Logged Out.")
		return redirect("/admin-login-page")
	except:
		flash("ALREADY LOGGED OUT")
		return redirect("/admin-login")


@app.route("/admin-dashboard",methods=["GET","POST"])
@admin_login_required
def admin_dashboard():
    return render_template("dashboard.html")


@app.route("/admin-all-campaign",methods=["GET","POST"])
@admin_login_required
def admin_all_campaign():
    try:
        cc=Campaign.query.all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,sts=0)
    except:
        return render_template("error.html")

@app.route("/admin-brands",methods=["GET","POST"])
@admin_login_required
def admin_brands():
    try:
        cc=Brand_details.query.all()
        return render_template("list_brands.html",ii=cc)
    except:
        return render_template("error.html")


@app.route("/admin-influencers",methods=["GET","POST"])
@admin_login_required
def admin_influencers():
    try:
        cc=Influencer_details.query.all()
        return render_template("list_inf.html",ii=cc)
    except:
        return render_template("error.html")

@app.route("/admin-filter_content/<int:sts>",methods=["GET","POST"])
@admin_login_required
def admin_filter_content(sts):
    try:
        # sts=request.form['status']
        typ=request.form['type']
        ptf=request.form['platform']
        cc=Campaign.query.filter_by(status=sts,subtype=typ,platform=ptf).all()
        d=[]
        for i in cc:
            b=Brand_details.query.filter_by(brand_id=i.brand_id).first()
            d.append({'c':i, 'brand_name':b.brand_name})
        return render_template("campaign.html",dd=d,status=status,sts=sts)
    except:
        return render_template("error.html")


@app.route("/admin-update-campaign-status/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_update_campaign_status(camp_id):
    try:
        if request.method=="POST":
            sts=request.form["status"]
            if sts==1:
                t1=Thread(target=send_active_msg, args=(camp_id,))
                t1.start()
            elif sts==2:
                t2=Thread(target=send_complete_msg, args=(camp_id,))
                t2.start()
            c=Campaign.query.filter_by(campaign_id=camp_id).first()
            c.status=sts
            if request.form["type1"]:
                type1=request.form["type1"]
                c.payout_influencers1=type1
            if request.form["type2"]:
                type2=request.form["type2"]
                c.payout_influencers2=type2
            if request.form["data"]:
                data=request.form["data"]
                c.data=data
            db.session.commit()
            flash("Submission Successfull..!!!")
            if sts=="0":
                return redirect("/admin-pending-campaign")
            elif sts=="1":
                return redirect("/admin-active-campaign")
            elif sts=="2":
                return redirect("/admin-completed-campaign")
        else:
            flash("Method not Allowed")
            return render_template("error.html")
    except:
        return render_template("error.html")

@app.route("/admin-influencers-involved/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_influencers_involved(camp_id):
    try:
        c=Influencers_involved.query.filter_by(campaign_id=camp_id).all()
        campaign=Campaign.query.filter_by(campaign_id=camp_id).first()
        return render_template("influencer_involved_list.html",ii=c,status=status,c=campaign)
    except:
        return render_template("error.html")

@app.route("/admin-get-post-data/<int:inf_id>",methods=["GET","POST"])
@admin_login_required
def admin_posts(inf_id):
    try:
        posts=Posts_done.query.filter_by(inf_inv_id=inf_id).all()
        return render_template("posts.html",ii=posts)
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-notdone/<int:post_id>/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_notdone(post_id,camp_id):
    try:
        post=Posts_done.query.filter_by(pd_id=post_id).first()
        post.done=False
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-done/<int:post_id>/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_done(post_id,camp_id):
    try:
        post=Posts_done.query.filter_by(pd_id=post_id).first()
        post.done=True
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-post-alldone/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_post_alldone(camp_id):
    try:
        influencer=Influencers_involved.query.filter_by(campaign_id=camp_id).all()
        for i in influencer:
            if (i.posts):
                if i.posts[0].post_unique_id:
                    i.posts[0].done=True
        db.session.commit()
        return redirect("/admin-influencers-involved/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-creative-upload/<int:camp_id>",methods=["GET","POST"])
def admin_creative_upload(camp_id):
    try:
        y=Campaign_posts.query.count()
        filename = 'admin_creative_'+str(camp_id)+"_"+str(y+1)+'.jpg'
        imageData=request.files['pfile'].read()
        with open('./static/images/'+filename, 'wb') as f:
            f.write(imageData)
            c=Campaign_posts(file_name=filename,approved=True,campaign_id=camp_id)
            db.session.add(c)
            db.session.commit()
            flash("Request creative uploaded ")
        return redirect("/admin-campaign-det/"+str(camp_id))
    except:
        return render_template("error.html")

@app.route("/admin-inf-det/<int:inf_id>",methods=["GET","POST"])
@admin_login_required
def admin_inf_det(inf_id):
    try:
        inf=Influencer_details.query.filter_by(influencer_id=inf_id).first()
        p=Payments.query.filter_by(influencer_id=inf_id).all()
        return render_template("inf_details.html",i=inf,p=p)
    except:
        return render_template("error.html")


@app.route("/admin-campaign-det/<int:campaign_id>",methods=["GET","POST"])
@admin_login_required
def admin_campaign_det(campaign_id):
    try:
        inf=Campaign.query.filter_by(campaign_id=campaign_id).first()
        return render_template("Camp_details.html",i=inf)
    except:
        return render_template("error.html")

@app.route("/admin-brand-det/<int:brand_id>",methods=["GET","POST"])
@admin_login_required
def admin_brand_det(brand_id):
    try:
        inf=Brand_details.query.filter_by(brand_id=brand_id).first()
        p=Payments.query.filter_by(brand_id=inf.brand_id).all()
        spoc=Spoc_details.query.filter_by(brand_id=inf.brand_id).first()
        return render_template("brand_det.html",i=inf,spoc=spoc,p=p)
    except:
        return render_template("error.html")


@app.route("/admin-payout/<int:camp_id>",methods=["GET","POST"])
@admin_login_required
def admin_payout(camp_id):
    try:
        c=Campaign.query.filter_by(campaign_id=camp_id).first()
        for i in c.influencers:
            if i.posts[0].done:
                fc=0
                paisa=0
                if c.platform==0:
                    fb=Facebook.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=fb.follower_count
                elif c.platform==1:
                    fb=Instagram.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=fb.follower_count
                elif c.platform==2:
                    fb=Twitter.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=fb.follower_count
                elif c.platform==3:
                    fb=Youtube.query.filter_by(influencer_id=i.influencer_id).first()
                    if fb:
                        fc=fb.subscriber_count
                if fc>99 and fc<501:
                    paisa=c.payout_influencers1
                elif fc>500:
                    paisa=c.payout_influencers2
                inf=Influencer_details.query.filter_by(influencer_id=i.influencer_id).first()
                inf.i_wallet=inf.i_wallet+int(paisa)
                db.session.commit()
        flash("Paid Successfully in wallet of Influencers")
        return render_template("error.html")
    except:
        return render_template("error.html")














app.secret_key="hello world is the most used phrase in coding background"
if __name__ == "__main__":
    app.run(debug=True)
