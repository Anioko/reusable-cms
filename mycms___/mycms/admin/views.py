"""Admin views."""
import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    flash, current_app, )
from wtforms.validators import Optional

from libs import GitUtils
from mycms.decorators import admin_required, anonymous_required
from .forms import AdminLoginForm, UserCrudForm, ModuleCrudForm, SlideShowCrudForm, SeoCrudForm, HomeTextForm, TechnologiesForm, ImageTechnologyForm, WebsiteLogoForm, FooterTextForm, SocialIocnForm, CopyRightForm, FooterImageForm, ResourcesForm, ResourceDetailAddForm
from mycms.user.models import User
from flask_login import login_user
from mycms.extensions import db
from .models import Module, SlideShowImage, Seo, ModuleImage, Setting, HomeText, TechnologiesImage, TechnologiesText, Logo, FooterText, FooterImage, SocialMediaIcon, CopyRight, Resource, ResourceDetail
from flask_uploads import UploadSet, IMAGES

from ..utils import sync_cart, get_setting_val

blueprint = Blueprint("admin", __name__, url_prefix="/admin", static_folder="../static")
images = UploadSet('images', IMAGES)


@blueprint.route("/", methods=["GET", "POST"])
@admin_required
def index():
    return render_template("admin/index.html")


@blueprint.route("/login/",  methods=["GET", "POST"])
@anonymous_required
def login():
    form = AdminLoginForm(request.form) 
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            sync_cart()
            redirect_url = url_for("admin.index")
            return redirect(redirect_url)
    return render_template("admin/login.html", form=form)

# ############### CRUD ################


# Admins CRUD
@blueprint.route("/admins/", defaults={"page": 1})
@blueprint.route("/admins/<int:page>")
@admin_required
def admin_list(page):
    admins = User.query.filter_by(is_admin=True).paginate(page, per_page=40)
    return render_template("admin/admins/admins_list.html", admins=admins)


@blueprint.route("/admins/add_admin/", methods=["GET", "POST"])
@admin_required
def admin_add():
    form = UserCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            User.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                active=True,
                is_admin=True,
            )
            flash("Admin Added Successfully .", "success")
            return redirect(url_for("admin.admin_list"))
    return render_template("admin/admins/admins_add.html", form=form)


@blueprint.route("/admins/update/<int:admin_id>/", methods=["GET", "POST"])
@admin_required
def admin_update(admin_id):
    admin = User.query.get_or_404(admin_id)
    form = UserCrudForm(obj=admin)
    form.password.validators = form.password.validators[1:]
    form.password.validators.insert(0, Optional())
    form.password.flags.required = False
    form.confirm.validators = form.confirm.validators[1:]
    form.confirm.validators.insert(0, Optional())
    form.confirm.flags.required = False

    if request.method == 'POST':
        if form.validate_on_submit():
            admin.username = form.username.data
            admin.email = form.email.data
            admin.first_name = form.first_name.data
            admin.last_name = form.last_name.data
            if form.password.data:
                admin.set_password(form.password.data)
            db.session.add(admin)
            db.session.commit()
            flash("Admin Updated Successfully", "success")
            return redirect(url_for('admin.admin_list'))
    return render_template("admin/admins/admins_update.html", admin=admin, form=form)


@blueprint.route("/admins/delete/<int:admin_id>/", methods=["POST"])
@admin_required
def admin_delete(admin_id):
    if admin_id == 0: # bulk delete
        admin_ids = request.form.get('ids[]').split(',')
        admins = User.query.filter(User.id.in_(admin_ids)).all()
    else:
        admins = [User.query.get_or_404(admin_id)]
    for admin in admins: db.session.delete(admin)
    db.session.commit()
    flash("Admins Deleted Successfully", "success")
    return redirect(url_for('admin.admin_list'))


# Clients CRUD
@blueprint.route("/users/", defaults={'page': 1})
@blueprint.route("/users/<int:page>")
@admin_required
def user_list(page):
    users = User.query.filter_by(is_admin=False).paginate(page, per_page=40)
    return render_template("admin/users/users_list.html", users=users)


@blueprint.route("/users/add_user/", methods=["GET", "POST"])
@admin_required
def user_add():
    form = UserCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            User.create(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                active=True,
                is_admin=False,
            )
            flash("Client Added Successfully .", "success")
            return redirect(url_for("admin.user_list"))
    return render_template("admin/users/users_add.html", form=form)


@blueprint.route("/users/update/<int:user_id>/", methods=["GET", "POST"])
@admin_required
def user_update(user_id):
    user = User.query.get_or_404(user_id)
    form = UserCrudForm(obj=user)
    form.password.validators = form.password.validators[1:]
    form.password.validators.insert(0, Optional())
    form.password.flags.required = False
    form.confirm.validators = form.confirm.validators[1:]
    form.confirm.validators.insert(0, Optional())
    form.confirm.flags.required = False
    
    if request.method == 'POST':
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Client Updated Successfully", "success")
            return redirect(url_for('admin.user_list'))
        
    return render_template("admin/users/users_update.html", user=user, form=form)


@blueprint.route("/users/delete/<int:user_id>/", methods=["POST"])
@admin_required
def user_delete(user_id):
    if user_id == 0: # bulk delete
        user_ids = request.form.get('ids[]').split(',')
        users = User.query.filter(User.id.in_(user_ids)).all()
    else:
        users = [User.query.get_or_404(user_id)]
    for user in users: db.session.delete(user)
    db.session.commit()
    flash("Clients Deleted Successfully", "success")
    return redirect(url_for('admin.user_list'))


#  Modules CRUD
@blueprint.route("/modules/", defaults={'page': 1})
@blueprint.route("/modules/<int:page>")
@admin_required
def module_list(page):
    modules = Module.query.paginate(page, per_page=40)
    return render_template("admin/modules/modules_list.html", modules=modules)


@blueprint.route('/modules/add_module', methods=['GET', 'POST'])
@admin_required
def module_add():
    form = ModuleCrudForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image = images.save(request.files['image'])
            module = Module.create(
                name=form.name.data,
                description=form.description.data,
                demo_url=form.demo_url.data,
                code_path=form.code_path.data,
                price=form.price.data,
                support_price=form.support_price.data,
                image_filename=image
            )
            db.session.add(module)
            db.session.commit()
            db.session.refresh(module)
            for image in request.files.getlist('images'):
                image_filename = images.save(image)
                ModuleImage.create(
                    module=module,
                    image_filename=image_filename
                )
            flash("Module Added Successfully .", "success")
            return redirect(url_for("admin.module_list"))
    return render_template("admin/modules/modules_add.html", form=form)


@blueprint.route('/modules/update_module/<int:module_id>', methods=['GET', 'POST'])
@admin_required
def module_update(module_id):
    module = Module.query.get_or_404(module_id)
    form = ModuleCrudForm(obj=module)
    form.images.validators = form.images.validators[1:]
    form.images.validators.insert(0, Optional())
    form.images.flags.required = False
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False

    if request.method == 'POST':
        if form.validate_on_submit():
            module.name = form.name.data
            module.description = form.description.data
            module.demo_url = form.demo_url.data
            module.code_path = form.code_path.data
            module.price = form.price.data
            module.support_price = form.support_price.data
            module.long_description = form.long_description.data
            module.tags = form.tags.data
            module.release_date = form.release_date.data
            module.last_update_date = form.last_update_date.data
            if request.files['image']:
                image = images.save(request.files['image'])
                if os.path.exists(module.image_path):
                    os.remove(module.image_path)
                module.image_filename = image
            db.session.add(module)
            db.session.commit()
            try:
                image_ids = request.form.getlist('old_images[]')
            except:
                image_ids = []
            for image in module.images:
                if str(image.id) not in image_ids:
                    if os.path.exists(image.image_path):
                        os.remove(image.image_path)
                    db.session.delete(image)
            if request.files['images']:
                for image in request.files.getlist('images'):
                    image_filename = images.save(image)
                    module_image = ModuleImage.create(
                        module=module,
                        image_filename=image_filename
                    )
                    db.session.add(module_image)
            db.session.commit()
            flash("Module Updated Successfully", "success")
            return redirect(url_for('admin.module_list'))

    return render_template("admin/modules/modules_update.html", module=module, form=form)


@blueprint.route('/modules/delete_module/<int:module_id>', methods=['GET', 'POST'])
@admin_required
def module_delete(module_id):
    if module_id == 0:  # bulk delete
        module_ids = request.form.get('ids[]').split(',')
        modules = Module.query.filter(Module.id.in_(module_ids)).all()
    else:
        modules = [Module.query.get_or_404(module_id)]
    for module in modules: db.session.delete(module)
    db.session.commit()
    flash("Modules Deleted Successfully", "success")
    return redirect(url_for('admin.module_list'))


# SlideShow CRUD
@blueprint.route("/slideshows/",defaults={'page': 1})
@blueprint.route("/slideshows/<int:page>")
@admin_required
def slideshow_list(page):
    slideshows = SlideShowImage.query.paginate(page, per_page=40)
    return render_template("admin/slideshows/slideshows_list.html", slideshows=slideshows)


@blueprint.route('/slideshows/add_slideshow', methods=['GET', 'POST'])
@admin_required
def slideshow_add():
    form = SlideShowCrudForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            image = images.save(request.files['image'])
            slideshow = SlideShowImage(title=title,image_filename=image)
            db.session.add(slideshow)
            db.session.commit()
            flash("SlideShow Added Successfully .", "success")
            return redirect(url_for("admin.slideshow_list"))
    
    return render_template("admin/slideshows/slideshows_add.html", form=form)


# SOmething is Wrong Here
@blueprint.route('/slideshows/slideshow_update/<int:slideshow_id>', methods=['GET', 'POST'])
@admin_required
def slideshow_update(slideshow_id):
    slideshow = SlideShowImage.query.get(slideshow_id)
    form = SlideShowCrudForm(obj=slideshow)
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            slideshow.title = title
            if request.files['image']:
                image = images.save(request.files['image'])
                if os.path.exists(slideshow.image_path):
                    os.remove(slideshow.image_path)
                slideshow.image_filename = image
            db.session.add(slideshow)
            db.session.commit()
            flash("SlideShow Updated Successfully .", "success")
            return redirect(url_for("admin.slideshow_list"))



    return render_template('admin/slideshows/slideshows_update.html', form=form, slideshow=slideshow)




@blueprint.route('/slideshows/delete_slideshow/<int:slideshow_id>', methods=['GET', 'POST'])
@admin_required
def slideshow_delete(slideshow_id):
    if slideshow_id == 0:  # bulk delete
        slideshows_ids = request.form.get('ids[]').split(',')
        slideshows = SlideShowImage.query.filter(SlideShowImage.id.in_(slideshows_ids)).all()
    else:
        slideshows = [SlideShowImage.query.get_or_404(slideshow_id)]
    for slideshow in slideshows: db.session.delete(slideshow)
    db.session.commit()
    flash("SlideShows Deleted Successfully", "success")
    return redirect(url_for('admin.slideshow_list'))


# SEO CRUD
@blueprint.route("/seo/",defaults={'page': 1})
@blueprint.route("/seo/<int:page>")
@admin_required
def seo_list(page):
    seos = Seo.query.paginate(page, per_page=40)
    return render_template("admin/seos/seos_list.html", seos=seos)


@blueprint.route('/seos/add_seo', methods=['GET', 'POST'])
@admin_required
def seo_add():
    form = SeoCrudForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            Seo.create(
                meta_tag=form.meta_tag.data,
                title=form.title.data,
                content=form.content.data,
            )

            flash("SEO Famous Words Added Successfully .", "success")
            return redirect(url_for("admin.seo_list"))
    return render_template('admin/seos/seos_add.html', form=form)


@blueprint.route('/seos/update_seo/<int:seo_id>', methods=['GET', 'POST'])
@admin_required
def seo_update(seo_id):
    seo = Seo.query.get_or_404(seo_id)
    form = SeoCrudForm(obj=seo)
    if request.method == 'POST':
        if form.validate_on_submit():
            seo.meta_tag = form.meta_tag.data
            seo.title = form.title.data
            seo.content = form.content.data
            db.session.add(seo)
            db.session.commit()
            flash("SEO Words/Tags Updated Successfully", "success")
            return redirect(url_for('admin.seo_list'))

    return render_template("admin/seos/seos_update.html", seo=seo, form=form)


@blueprint.route('/seos/delete_seo/<int:seo_id>', methods=['GET', 'POST'])
@admin_required
def seo_delete(seo_id):
    if seo_id == 0:  # bulk delete
        seo_ids = request.form.get('ids[]').split(',')
        seos = Seo.query.filter(Seo.id.in_(seo_ids)).all()
    else:
        seos = [Seo.query.get_or_404(seo_id)]
    for seo in seos: db.session.delete(seo)
    db.session.commit()
    flash("SEO words  Deleted Successfully", "success")
    return redirect(url_for('admin.seo_list'))


@blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    available_settings = current_app.config['AVAILABLE_ADMIN_SETTINGS']
    available_settings_keys = [key[0] for key in available_settings]
    settings_objects = Setting.query.filter(Setting.name.in_(available_settings_keys)).all()
    current_app.logger.info(available_settings_keys)
    current_app.logger.info(settings_objects)
    if len(settings_objects) != len(available_settings):
        for setting in available_settings:
            get_setting_val(setting)
        settings_objects = Setting.query.filter(Setting.name.in_(available_settings_keys)).all()
    if request.method == 'POST':
        for setting in available_settings:
            setting_obj = get_setting_val(setting)
            setting_val = request.form.get(setting[0])
            if not setting_val:
                flash("Wrong value for {}".format(setting[1]), 'danger')
                return redirect(url_for('admin.settings'))
            setting_obj.value = setting_val
            db.session.add(setting_obj)
        db.session.commit()
        flash("Settings updated successfully", 'success')
        return redirect(url_for('admin.settings'))
    current_app.logger.info(settings_objects)
    return render_template('admin/settings.html', settings=settings_objects)

###############################################################################
###############################################################################

# HomeText For Public Front END
@blueprint.route('/home', methods=['POST', 'GET'])
@admin_required
def hometext():
    home_title = HomeText.query.all()
    return render_template('admin/public/hometext.html', home_data=home_title)


# Add home tille 
@blueprint.route('/home/home_title_add', methods=['POST', 'GET'])
@admin_required
def addhometext():
    form = HomeTextForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            HomeText.create(
                firstext=form.firstext.data,
                secondtext=form.secondtext.data,
            )
            flash("Home Text Added Successfully.", "success")
            return redirect(url_for("admin.hometext"))
    return render_template('admin/public/add_home_title.html', form=form)


# Update home title
@blueprint.route('/home/update_title/<int:id>/', methods=['POST', 'GET'])
@admin_required
def update_home_title(id):
    home = HomeText.query.get_or_404(id)
    form = HomeTextForm(obj=home)
    if form.validate_on_submit():
        home.firstext = form.firstext.data
        home.secondtext = form.secondtext.data
        db.session.add(home)
        db.session.commit()
        flash("Home Title updated Successfully", "success")
        return redirect(url_for('admin.hometext'))
    return render_template('admin/public/update_home_title.html', home=home, form=form)


# Delete Home title Record 
@blueprint.route('/home/delete_title/<int:title_id>', methods=['GET', 'POST'])
@admin_required
def home_delete(title_id):
    title = HomeText.query.get_or_404(title_id) 
    db.session.delete(title)
    db.session.commit()
    flash("Home Title  Deleted Successfully", "success")
    return redirect(url_for('admin.hometext'))


# Technologies Text 
@blueprint.route('/technologies', methods=['POST', 'GET'])
@admin_required
def technologies_home():
    obj = TechnologiesText.query.all()
    return render_template('admin/public/technologies/technologies_list.html', home_data=obj)


# Add Technologies
@blueprint.route('/technologies/add', methods=['POST', 'GET'])
@admin_required
def add_technologies():
    form = TechnologiesForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            TechnologiesText.create(
                firstext = form.firstext.data,
                secondtext = form.secondtext.data,
            )
            flash("Technologies Text Added Successfully.", "success")
            return redirect(url_for("admin.technologies_home"))
    return render_template('admin/public/technologies/add_techno.html', form=form)


# Update Technologies
@blueprint.route('/technologies/update/<int:title_id>', methods=['POST', 'GET'])
@admin_required
def update_technologies(title_id):
    data = TechnologiesText.query.get_or_404(title_id)
    form = TechnologiesForm(obj=data)
    if form.validate_on_submit():
        data.firstext = form.firstext.data
        data.secondtext = form.secondtext.data
        db.session.add(data)
        db.session.commit()
        flash("Technologies Title updated Successfully", "success")
        return redirect(url_for('admin.technologies_home'))
    return render_template('admin/public/technologies/update_techno.html', data=data, form=form)


# Delete Technologies 
@blueprint.route('/technologies/delete/<int:title_id>', methods=['POST', 'GET'])
@admin_required
def delete_technologies(title_id):
    data = TechnologiesText.query.get_or_404(title_id)
    db.session.delete(data)
    db.session.commit()
    flash("Technologies Title Deleted Successfully", "success")
    return redirect(url_for('admin.technologies_home'))


# Technologies Image save
@blueprint.route('/technology_image', methods=['POST', 'GET'])
@admin_required
def technology_image():
    images = TechnologiesImage.query.all()
    return render_template('admin/public/technology_image/technology_list.html', images=images)


# Technology add with image 
@blueprint.route('/technology_image/add', methods=['POST', 'GET'])
@admin_required
def add_technology_image():
    form = ImageTechnologyForm()
    if request.method == 'POST':
        image = images.save(request.files['image'])
        technology_img = TechnologiesImage(image=image)
        db.session.add(technology_img)
        db.session.commit()
        flash("Technology Added Successfully .", "success")
        return redirect(url_for('admin.technology_image'))
    return render_template('admin/public/technology_image/technology_add.html', form=form)



@blueprint.route('/technology_image/update/<int:image_id>', methods=['POST', 'GET'])
@admin_required
def update_techno_image(image_id):
    image_data = TechnologiesImage.query.get(image_id)
    form = ImageTechnologyForm(obj=image_data)
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False
    if request.method == 'POST':
        if request.files['image']:
            image = images.save(request.files['image'])
            if os.path.exists(image_data.image_path):
                os.remove(image_data.image_path)
            image_data.image_filename = image
        db.session.add(image_data)
        db.session.commit()
        flash("Technology Image Updated Successfully.", "success")
        return redirect(url_for("admin.technology_image"))
    return render_template("admin/public/technology_image/techno_update_img.html", form=form, image_data=image_data)


# delete image 
@blueprint.route('/technology_image/delete/<int:image_id>', methods=['GET', 'POST'])
@admin_required
def delete_image(image_id):
    data = TechnologiesImage.query.get(image_id)
    db.session.delete(data)
    db.session.commit()
    flash("Technology Image deleted Successfully.", "success")
    return redirect(url_for('admin.technology_image'))


# Website Logo 
@blueprint.route('/logo', methods=['GET', 'POST'])
@admin_required
def logo_home():
    data = Logo.query.all()
    return render_template('admin/public/logo/logo_list.html', data=data)


# Logo add method
@blueprint.route('/logo/add', methods=['POST', 'GET'])
@admin_required
def add_logo():
    form = WebsiteLogoForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['logo_image'])
        logo = Logo(logo_image=image)
        db.session.add(logo)
        db.session.commit()
        flash("Logo Added Successfully .", "success")
        return redirect(url_for('admin.logo_home'))
    return render_template('admin/public/logo/add_logo.html', form=form)


# Logo Delete Method 
@blueprint.route('/logo/delete/<int:logo_id>', methods=['POST', 'GET'])
@admin_required
def delete_logo(logo_id):
    logo_data = Logo.query.get(logo_id)
    db.session.delete(logo_data)
    db.session.commit()
    flash("Logo Deleted Successfully.", "success")
    return redirect(url_for('admin.logo_home'))
    

# Privacy Information
@blueprint.route('/privacy', methods=['POST', 'GET'])
@admin_required
def privacy_home():
    footer_text = FooterText.query.all()
    icons = SocialMediaIcon.query.all()
    copyright_text = CopyRight.query.all()
    footer_image = FooterImage.query.all()
    resources = Resource.query.all()
    return render_template('admin/public/privacy/privacy_home.html', resources=resources, footer_text=footer_text, icons=icons, text=copyright_text, footer_image=footer_image)


# Footer text add
@blueprint.route('/privacy/footer_text/add', methods=['POST', 'GET'])
@admin_required
def footer_text_add():
    form = FooterTextForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            FooterText.create(title=form.title.data)
            flash("Footer Text Title Save SuccessFully.", "success")
            return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/footer_text/footer_text.html', form=form)


#Footer Text Update Function
@blueprint.route('/privacy/footer_text/edit/<int:text_id>', methods=['POST', 'GET'])
@admin_required
def footer_text_update(text_id):
    data = FooterText.query.get(text_id)
    form = FooterTextForm(obj=data)
    if form.validate_on_submit():
        data.title = form.title.data
        db.session.add(data)
        db.session.commit()
        flash("Footer text Updated Successfully.", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/footer_text/footer_text_update.html', form=form, data=data)


# Footer Title add Function
@blueprint.route('/privacy/footer_text/delete/<int:text_id>', methods=['POST', 'GET'])
@admin_required
def footer_text_delete(text_id):
    footer_text_id = FooterText.query.get(text_id)
    db.session.delete(footer_text_id)
    db.session.commit()
    flash("Footer text Title Add Suucessfully.", "success")
    return redirect(url_for('admin.privacy_home'))



# Social Media icon and link add
@blueprint.route('/privacy/social_icon/add', methods=['POST', 'GET'])
@admin_required
def icon_add():
    form = SocialIocnForm(request.form)
    if request.method == 'POST':
        # image = images.save(request.files['image'])
        icon = form.icon.data
        icon_link = form.url_link.data
        data = SocialMediaIcon(icon=icon, url_link=icon_link)
        db.session.add(data)
        db.session.commit()
        flash("Social Media Icon Add Successfully.", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/media_icon/icon_add.html', form=form)


# Social Media icon and link Update 
@blueprint.route('/privacy/social_icon/edit/<int:icon_id>', methods=['POST', 'GET'])
@admin_required
def icon_update(icon_id):
    data = SocialMediaIcon.query.get(icon_id)
    form = SocialIocnForm(obj=data)
    if form.validate_on_submit():
        data.icon = form.icon.data
        data.url_link = form.url_link.data
        db.session.add(data)
        db.session.commit()
        flash("Social Media iocn and link Update.", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/media_icon/icon_update.html', form=form, data=data)


# Social media icon delete function
@blueprint.route('/privacy/social_icon/delete/<int:icon_id>', methods=['POST', 'GET'])
@admin_required
def icon_delete(icon_id):
    icon = SocialMediaIcon.query.get(icon_id)
    db.session.delete(icon)
    db.session.commit()
    flash("Social Media Icon Deleted Successfully.", "success")
    return redirect(url_for('admin.privacy_home'))


# Copyright add for footer function
@blueprint.route('/privacy/copyright/add', methods=['POST', 'GET'])
def copyright_add():
    form = CopyRightForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            text = form.text.data
            obj = CopyRight(text=text)
            db.session.add(obj)
            db.session.commit()
            flash("CopyRight Footer text Save Successfully.", "success")
            return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/copyright/copyright_add.html', form=form)


# Copyright text Edit 
@blueprint.route('/privacy/copyright/edit/<int:copytext_id>', methods=['POST', 'GET'])
@admin_required
def copyright_edit(copytext_id):
    data = CopyRight.query.get(copytext_id)
    form = CopyRightForm(obj=data)
    if form.validate_on_submit():
        data.text = form.text.data
        db.session.add(data)
        db.session.commit()
        flash("Copyright footer Updated SuccessFully.", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/copyright/copyright_update.html', form=form, data=data)



# Copyright Footer text Delete 
@blueprint.route('/privacy/copyright/delete/<int:copytext_id>', methods=['POST', 'GET'])
@admin_required
def copyright_delete(copytext_id):
    obj = CopyRight.query.get(copytext_id)
    db.session.delete(obj)
    db.session.commit()
    flash("Copyright Footer text Delete Successfully.", "success")
    return redirect(url_for('admin.privacy_home'))


# Footer image add
@blueprint.route('/privacy/footer_image/add', methods=['POST', 'GET'])
@admin_required
def footer_image_add():
    form = FooterImageForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['image'])
        data = FooterImage(image=image)
        db.session.add(data)
        db.session.commit()
        flash("Footer Image save successfully.", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/footer_image/image_add.html', form=form)


# Footer image delete 
@blueprint.route('/privacy/footer_image/delete/<int:image_id>', methods=['POST', 'GET'])
@admin_required
def footer_image_delete(image_id):
    data = FooterImage.query.get(image_id)
    db.session.delete(data)
    db.session.commit()
    flash("Footer Image deleted Successfully.", "success")
    return redirect(url_for('admin.privacy_home'))


# Resource text Add function
@blueprint.route('/privacy/resource/add', methods=['POST', 'GET'])
def resource_add():
    form = ResourcesForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            role_title = form.role_title.data
            data = Resource(role_title=role_title)
            db.session.add(data)
            db.session.commit()
            flash("Resource Role title Add SuccessFully.", "success")
            return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/resource/resource_add.html', form=form)


# resources update function
@blueprint.route('/privacy/resource/edit/<int:role_id>', methods=['POST', 'GET'])
@admin_required
def resource_update(role_id):
    get_obj = Resource.query.get(role_id)
    form = ResourcesForm(obj=get_obj)
    if form.validate_on_submit():
        get_obj.role_title = form.role_title.data
        db.session.add(get_obj)
        db.session.commit()
        flash("Resource Role title Updated Successfully", "success")
        return redirect(url_for('admin.privacy_home'))
    return render_template('admin/public/resource/resource_update.html', form=form)


# Resources Role title delete function 
@blueprint.route('/privacy/resource/delete/<int:role_id>', methods=['POST', 'GET'])
@admin_required
def resource_delete(role_id):
    data = Resource.query.get(role_id)
    db.session.delete(data)
    db.session.commit()
    flash("Resources Role Deleted Successfully.", "success")
    return redirect(url_for('admin.privacy_home'))


# Resource Role get Details
@blueprint.route('/privacy/resource/details', methods=['POST', 'GET'])
@admin_required
def resource_details():
    # data = Resource.query.get(resource_id)
    form = ResourceDetailAddForm()
    data = request.form.get('role_name')
    details = ResourceDetail.query.filter_by(resource_id=int(data)).first()
    if details:
        form = ResourceDetailAddForm(obj=details)
        return render_template('admin/public/resource/resource_role_update.html', form=form)
    role_id = Resource.query.get(int(data))
    return render_template('admin/public/resource/resource_role_add.html', form=form, role_id=role_id)


# # Resource Detail Update Functions
# @blueprint.route('/privacy/resource/update/<int:role_id>', methods=['GET', 'POST'])
# @admin_required
# def resource_detail_update(resource_id):


# Resource Detail Add new function
@blueprint.route('/privacy/resource/details/add/<int:role_id>', methods=['POST', 'GET'])
@admin_required
def resource_new_add(role_id):
    form = ResourceDetailAddForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            desc = form.description.data
            data = ResourceDetail(title=title, description=desc, resource_id=role_id)
            db.session.add(data)
            db.session.commit()
            flash("Resource Details New Add Successfully.", "success")
            return redirect(url_for("admin.privacy_home"))