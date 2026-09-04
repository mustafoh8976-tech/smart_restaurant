from database.db_connect import get_connect


async def init_tables():
    conn = await get_connect()
    try:
        await conn.execute('''
        create table if not exists users(
            id serial primary key,
            telegram_id bigint unique not null,
            first_name varchar(100),
            username varchar(100),
            phone varchar(30),
            email varchar(150),
            password_hash varchar(64),
            role varchar(20) default 'customer',
            created_at timestamp default now()
        );

        alter table users add column if not exists email varchar(150);
        alter table users add column if not exists password_hash varchar(64);

        create table if not exists categories(
            id serial primary key,
            name varchar(100) unique not null
        );

        insert into categories(name)
        values ('Блюда жидкие'), ('Блюда основные')
        on conflict(name) do nothing;

        delete from categories where trim(name) = '1';

        create table if not exists dishes(
            id serial primary key,
            category_id integer references categories(id) on delete cascade,
            name varchar(150) not null,
            description varchar(500),
            price numeric(10, 2) not null check(price >= 0),
            ingredients varchar(500),
            image varchar(500),
            is_available boolean default true
        );

        create table if not exists cart_items(
            id serial primary key,
            user_id bigint references users(telegram_id) on delete cascade,
            dish_id integer references dishes(id) on delete cascade,
            quantity integer not null check(quantity > 0),
            unique(user_id, dish_id)
        );

        create table if not exists orders(
            id serial primary key,
            user_id bigint references users(telegram_id) on delete cascade,
            delivery_type varchar(20) not null,
            address varchar(300),
            phone varchar(30) not null,
            comment varchar(500),
            total_price numeric(10, 2) not null check(total_price >= 0),
            status varchar(30) default 'new',
            created_at timestamp default now()
        );

        create table if not exists order_items(
            id serial primary key,
            order_id integer references orders(id) on delete cascade,
            dish_id integer references dishes(id),
            quantity integer not null check(quantity > 0),
            price numeric(10, 2) not null check(price >= 0)
        );

        create table if not exists restaurant_tables(
            id serial primary key,
            table_number integer unique not null,
            capacity integer not null check(capacity > 0),
            is_active boolean default true
        );

        create table if not exists reservations(
            id serial primary key,
            user_id bigint references users(telegram_id) on delete cascade,
            table_id integer references restaurant_tables(id),
            reservation_date date not null,
            reservation_time time not null,
            guests integer not null check(guests > 0),
            phone varchar(30) not null,
            comment varchar(500),
            status varchar(20) default 'pending',
            created_at timestamp default now(),
            unique(table_id, reservation_date, reservation_time)
        );

        create table if not exists favorites(
            id serial primary key,
            user_id bigint references users(telegram_id) on delete cascade,
            dish_id integer references dishes(id) on delete cascade,
            unique(user_id, dish_id)
        );

        create table if not exists feedback(
            id serial primary key,
            user_id bigint references users(telegram_id) on delete cascade,
            order_id integer references orders(id) on delete cascade,
            rating integer not null check(rating between 1 and 5),
            comment varchar(500),
            created_at timestamp default now(),
            unique(user_id, order_id)
        );
        ''')
    except Exception as error:
        print(f'table creation error: {error}')
    finally:
        await conn.close()
