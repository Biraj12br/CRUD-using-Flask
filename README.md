This is a project of designing REST APIs involving CRUD operation via FLASK webframework.
Amazon sales dataset is used in this project.
Data is cleaned and transformed according to the requirement and is stored in the database
SQLAlchemy module is used for database interaction and implemention ORM (Object Relational Mapping).
JWT implementation is also done in order to secure the end points.

The project also includes : 
Keeping refresh and access tokes in cookies for protecting them from XSS
JTI is used to blacklist the tokens.
Refresh token rotation is also done to increase the security of the end points 

