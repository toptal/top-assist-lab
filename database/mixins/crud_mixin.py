from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class CRUDMixin:
    def get_or_create(self, db_session: Session):
        try:
            filter_attrs = self.get_filter_attributes()
            filters = {attr: getattr(self, attr) for attr in filter_attrs}
            db_instance = db_session.query(type(self)).filter_by(**filters).first()

            if db_instance:
                return db_instance
            else:
                db_session.add(self)
                db_session.commit()
                db_session.refresh(self)
                return self

        except SQLAlchemyError as e:
            class_name = type(self).__name__
            print(f"Error in {class_name} get_or_create method: {e}")
            db_session.rollback()
            return None

    def update(self, db_session: Session):
        try:
            db_session.commit()
        except SQLAlchemyError as e:
            class_name = type(self).__name__
            print(f"Error in {class_name} update method: {e}")
            db_session.rollback()

    def get_filter_attributes(self):
        """
        This method should be overridden by child classes to return a list of attribute names
        used for filtering when performing get_or_create operation.
        We use the filtering to identify if the object should be fetched or created
        """
        raise NotImplementedError(
            "'get_filter_attributes' method must be implemented in child classes."
        )

    def create_or_update(self, db_session: Session, **kwargs):
        try:
            filter_attrs = self.get_filter_attributes()
            filters = {attr: kwargs.get(attr) for attr in filter_attrs if kwargs.get(attr) is not None}
            db_instance = db_session.query(type(self)).filter_by(**filters).first()

            if db_instance:
                # Update existing instance
                for key, value in kwargs.items():
                    setattr(db_instance, key, value)
                db_session.commit()
                db_session.refresh(db_instance)
                return db_instance
            else:
                # Create new instance
                new_instance = type(self)(**kwargs)
                db_session.add(new_instance)
                db_session.commit()
                db_session.refresh(new_instance)
                return new_instance
        except SQLAlchemyError as e:
            class_name = type(self).__name__
            print(f"Error in {class_name} create_or_update method: {e}")
            db_session.rollback()
            return None
