DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS like;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS tag;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  photo TEXT,
  likes INTEGER DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE like (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL ,
  FOREIGN KEY (post_id) REFERENCES post (id),
  FOREIGN KEY (user_id) REFERENCES user (id),
  UNIQUE (user_id, post_id)
);

CREATE TABLE comment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE tag (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post (id)
);

-- Trigger
CREATE TRIGGER count_likes_after_insert
         AFTER INSERT
            ON [like]
BEGIN
    UPDATE post
       SET likes = (
               SELECT COUNT( * )
                 FROM [like]
                WHERE post_id = NEW.post_id
           )
     WHERE id = NEW.post_id;
END;

CREATE TRIGGER count_likes_after_delete
         AFTER DELETE
            ON [like]
BEGIN
    UPDATE post
       SET likes = (
               SELECT COUNT( * )
                 FROM [like]
                WHERE post_id = OLD.post_id
           )
     WHERE id = OLD.post_id;
END;

INSERT INTO user(username, password) VALUES ('TEST01', '123');
INSERT INTO user(username, password) VALUES ('TEST02', '123');
INSERT INTO user(username, password) VALUES ('TEST03', '123');

INSERT INTO post(author_id, title, body) VALUES(1, '테스트 포스팅01', '테스트');
INSERT INTO post(author_id, title, body) VALUES(1, '테스트 포스팅02', '테스트');
INSERT INTO post(author_id, title, body) VALUES(2, '테스트 포스팅03', '테스트');

INSERT INTO tag(post_id, body) VALUES(1, '테스트');
INSERT INTO tag(post_id, body) VALUES(1, '테스트2');

INSERT INTO comment(post_id, user_id, body) VALUES(1, 2, '테스트 댓글');
INSERT INTO comment(post_id, user_id, body) VALUES(1, 2, '테스트 댓글');
INSERT INTO comment(post_id, user_id, body) VALUES(1, 3, '테스트 댓글');

INSERT INTO like(post_id, user_id) VALUES(1,1);
INSERT INTO like(post_id, user_id) VALUES(1,2);
INSERT INTO like(post_id, user_id) VALUES(1,3);
