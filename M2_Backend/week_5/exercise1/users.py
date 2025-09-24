from utilities.db import PgManager


def create_users(db_manager: PgManager):
    db_manager.execute_query(
        """
        CREATE TABLE account_status (
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE
        );
        """
    )

    db_manager.execute_query(
        """
        CREATE TABLE users(
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(30),
            email VARCHAR(35),
            username VARCHAR(30),
            password VARCHAR(30),
            birthday DATE,
            account_status_id INT REFERENCES account_status(id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO account_status (name) VALUES
        ('activo'),
        ('suspendido'),
        ('moroso');
        """
    )

    db_manager.execute_query(
        """
        INSERT INTO users (full_name, email, username, password, birthday, account_status_id) VALUES
        ('Lucas Smith', 'lucas.smith1@mail.com', 'lucas_smith1', 'Qw3rty!9', '1990-04-12', 1),
        ('Emma Johnson', 'emma.johnson2@mail.com', 'emma_johnson2', 'Pa$$word2', '1988-11-23', 2),
        ('Mateo Brown', 'mateo.brown3@mail.com', 'mateo_brown3', 'XyZ12345', '1995-07-30', 3),
        ('Olivia Garcia', 'olivia.garcia4@mail.com', 'olivia_garcia4', 'Ol1v1a!@', '1992-02-14', 1),
        ('Santiago Lee', 'santiago.lee5@mail.com', 'santiago_lee5', 'LeeS@nt22', '1991-09-05', 1),
        ('Valentina Kim', 'valentina.kim6@mail.com', 'valentina_kim6', 'ValK!m2021', '1993-12-19', 3),
        ('Benjamin Clark', 'benjamin.clark7@mail.com', 'benjamin_clark7', 'BenC#2022', '1989-06-08', 2),
        ('Mia Lewis', 'mia.lewis8@mail.com', 'mia_lewis8', 'MiaL*123', '1996-03-27', 1),
        ('Sebastian Walker', 'sebastian.walker9@mail.com', 'sebastian_walker9', 'SebW@lk9', '1994-10-16', 3),
        ('Sofia Hall', 'sofia.hall10@mail.com', 'sofia_hall10', 'SofH!2020', '1990-01-02', 1),
        ('David Young', 'david.young11@mail.com', 'david_young11', 'DavY0ung!', '1987-08-21', 2),
        ('Isabella Allen', 'isabella.allen12@mail.com', 'isabella_allen12', 'IsaA#l12', '1992-05-11', 3),
        ('Gabriel King', 'gabriel.king13@mail.com', 'gabriel_king13', 'GabK!ng13', '1993-11-29', 1),
        ('Camila Wright', 'camila.wright14@mail.com', 'camila_wright14', 'CamWri14$', '1991-07-07', 1),
        ('Samuel Scott', 'samuel.scott15@mail.com', 'samuel_scott15', 'SamS!c15', '1995-02-18', 3),
        ('Victoria Green', 'victoria.green16@mail.com', 'victoria_green16', 'VicG#r16', '1989-12-03', 2),
        ('Daniel Adams', 'daniel.adams17@mail.com', 'daniel_adams17', 'DanA!d17', '1994-09-25', 1),
        ('Martina Baker', 'martina.baker18@mail.com', 'martina_baker18', 'MarB@k18', '1990-06-13', 3),
        ('Nicolas Nelson', 'nicolas.nelson19@mail.com', 'nicolas_nelson19', 'NicN#l19', '1992-03-31', 1),
        ('Lucia Carter', 'lucia.carter20@mail.com', 'lucia_carter20', 'LucC!r20', '1996-08-09', 2),
        ('Diego Mitchell', 'diego.mitchell21@mail.com', 'diego_mitchell21', 'DieM!t21', '1991-01-17', 3),
        ('Elena Perez', 'elena.perez22@mail.com', 'elena_perez22', 'EleP#r22', '1993-04-28', 1),
        ('Tomas Roberts', 'tomas.roberts23@mail.com', 'tomas_roberts23', 'TomR@b23', '1995-11-12', 1),
        ('Renata Evans', 'renata.evans24@mail.com', 'renata_evans24', 'RenE!v24', '1988-10-04', 3),
        ('Juan Turner', 'juan.turner25@mail.com', 'juan_turner25', 'JuaT#r25', '1990-05-20', 2),
        ('Antonia Phillips', 'antonia.phillips26@mail.com', 'antonia_phillips26', 'AntP!h26', '1992-12-15', 1),
        ('Felipe Campbell', 'felipe.campbell27@mail.com', 'felipe_campbell27', 'FelC@p27', '1994-07-01', 3),
        ('Paula Parker', 'paula.parker28@mail.com', 'paula_parker28', 'PauP#k28', '1996-02-22', 1),
        ('Joaquin Edwards', 'joaquin.edwards29@mail.com', 'joaquin_edwards29', 'JoaE!d29', '1991-09-14', 2),
        ('Valeria Collins', 'valeria.collins30@mail.com', 'valeria_collins30', 'ValC@l30', '1993-06-06', 3),
        ('Emiliano Stewart', 'emiliano.stewart31@mail.com', 'emiliano_stewart31', 'EmiS#t31', '1995-03-19', 1),
        ('Josefina Sanchez', 'josefina.sanchez32@mail.com', 'josefina_sanchez32', 'JosS!z32', '1989-12-27', 2),
        ('Dylan Morris', 'dylan.morris33@mail.com', 'dylan_morris33', 'DylM@r33', '1992-08-15', 3),
        ('Florencia Rogers', 'florencia.rogers34@mail.com', 'florencia_rogers34', 'FloR#s34', '1994-05-03', 1),
        ('Bruno Reed', 'bruno.reed35@mail.com', 'bruno_reed35', 'BruR!d35', '1990-10-29', 1),
        ('Julieta Cook', 'julieta.cook36@mail.com', 'julieta_cook36', 'JulC@k36', '1991-04-11', 3),
        ('Maximo Morgan', 'maximo.morgan37@mail.com', 'maximo_morgan37', 'MaxM#n37', '1993-11-08', 2),
        ('Agustina Bell', 'agustina.bell38@mail.com', 'agustina_bell38', 'AguB!l38', '1995-06-24', 1),
        ('Facundo Murphy', 'facundo.murphy39@mail.com', 'facundo_murphy39', 'FacM@p39', '1988-09-17', 3),
        ('Catalina Bailey', 'catalina.bailey40@mail.com', 'catalina_bailey40', 'CatB#y40', '1992-01-06', 1),
        ('Juan Pablo Rivera', 'juan.rivera41@mail.com', 'juan_rivera41', 'JuaR!v41', '1994-08-13', 2),
        ('Amanda Cooper', 'amanda.cooper42@mail.com', 'amanda_cooper42', 'AmaC@p42', '1996-03-25', 3),
        ('Martin Richardson', 'martin.richardson43@mail.com', 'martin_richardson43', 'MarR#n43', '1991-12-02', 1),
        ('Jose Torres', 'jose.torres44@mail.com', 'jose_torres44', 'JosT!r44', '1993-07-21', 1),
        ('Manuela Cox', 'manuela.cox45@mail.com', 'manuela_cox45', 'ManC@x45', '1995-02-10', 3),
        ('Andres Ward', 'andres.ward46@mail.com', 'andres_ward46', 'AndW#d46', '1989-05-28', 2),
        ('Gabriela Brooks', 'gabriela.brooks47@mail.com', 'gabriela_brooks47', 'GabB!k47', '1992-10-18', 1),
        ('Leonardo James', 'leonardo.james48@mail.com', 'leonardo_james48', 'LeoJ@m48', '1994-01-30', 3),
        ('Mariah Bennett', 'mariah.bennett49@mail.com', 'mariah_bennett49', 'MarB#t49', '1996-06-07', 1),
        ('Pedro Wood', 'pedro.wood50@mail.com', 'pedro_wood50', 'PedW!d50', '1990-03-15', 2);
        """
    )
