create Table kenoZahlen(Datum date not Null primary key,z1 int not null ,
z2 int not null,z3 int not null,z4 int not null,z5 int not null,
z6 int not null,z7 int not null,z8 int not null,z9 int not null,
z10 int not null,z11 int not null,z12 int not null,z13 int not null,
z14 int not null,z15 int not null,z16 int not null,z17 int not null,
z18 int not null,z19 int not null,z20 int not null,Plus5 int not null,
						Spieleinsatz varchar(15)
); 
 COPY kenoZahlen(Datum,z1,z2,z3,z4,z5,z6,z7,z8,z9,z10,z11,z12,z13,z14,z15,z16,z17,z18,z19,z20,
				Plus5,  Spieleinsatz) 
FROM 'C:\Users\kenfu\Documents\KENO_ab_2018.xls (1)\kenoZahlen.csv' DELIMITER ';' CSV HEADER
;
alter table KenoZahlen add id serial Primary key;


		 
		 
		--comparaison von links-unten nach recht-oben  Diagonal 
		 select *
from (select t2.* --id, t2.Datum,t2.z1,t2.z2,t2.z3,t2.z4,t2.z5,t2.z6,t2.z7,t2.z8,t2.z9,t2.z10,t2.z11,t2.z12,t2.z13,t2.z14,t2.z15,t2.z16,t2.z17,t2.z18,t2.z19,t2.z20
	  from kenozahlen as t2 join kenozahlen as t1 on (t2.id-1)=t1.id 
where  ((t2.z1=t1.z2) or (t2.z2=t1.z3) or (t2.z3=t1.z4) or (t2.z4=t1.z5) or (t2.z5=t1.z6) or
	(t2.z6=t1.z7) or (t2.z7=t1.z8) or (t2.z8=t1.z9) or (t2.z9=t1.z10) or (t2.z10=t1.z11) or
	   (t2.z11=t1.z12) or (t2.z12=t1.z13) or (t2.z13=t1.z14) or (t2.z14=t1.z15) or (t2.z15=t1.z16) or
		 (t2.z16=t1.z17) or (t2.z17=t1.z18) or (t2.z18=t1.z19) or (t2.z19=t1.z20)  ) 
	 ) as T
	 where datum between '2019-10-14' and '2019-11-3'
	 
	 
	 
	 
	 --comparaison von links-oben nach recht-unten  Diagonal 
		 select *
from (select t2.* --id, t2.Datum,t2.z1,t2.z2,t2.z3,t2.z4,t2.z5,t2.z6,t2.z7,t2.z8,t2.z9,t2.z10,t2.z11,t2.z12,t2.z13,t2.z14,t2.z15,t2.z16,t2.z17,t2.z18,t2.z19,t2.z20
	  from kenozahlen as t2 join kenozahlen as t1 on (t2.id+1)=t1.id 
where  ((t2.z1=t1.z2) or (t2.z2=t1.z3) or (t2.z3=t1.z4) or (t2.z4=t1.z5) or (t2.z5=t1.z6) or
	(t2.z6=t1.z7) or (t2.z7=t1.z8) or (t2.z8=t1.z9) or (t2.z9=t1.z10) or (t2.z10=t1.z11) or
	   (t2.z11=t1.z12) or (t2.z12=t1.z13) or (t2.z13=t1.z14) or (t2.z14=t1.z15) or (t2.z15=t1.z16) or
		 (t2.z16=t1.z17) or (t2.z17=t1.z18) or (t2.z18=t1.z19) or (t2.z19=t1.z20)  ) 
	 ) as T
		 
		 
		-- comparaison vertical 
		 select datum,id
from (select t2.* --id, t2.Datum,t2.z1,t2.z2,t2.z3,t2.z4,t2.z5,t2.z6,t2.z7,t2.z8,t2.z9,t2.z10,t2.z11,t2.z12,t2.z13,t2.z14,t2.z15,t2.z16,t2.z17,t2.z18,t2.z19,t2.z20
	  from kenozahlen as t2 join kenozahlen as t1 on (t2.id-1)=t1.id 
where  ((t2.z1=t1.z1) or (t2.z2=t1.z2) or (t2.z3=t1.z3) or (t2.z4=t1.z4) or (t2.z5=t1.z5) or
	(t2.z6=t1.z6) or (t2.z7=t1.z7) or (t2.z8=t1.z8) or (t2.z9=t1.z9) or (t2.z10=t1.z10) or
	   (t2.z11=t1.z11) or (t2.z12=t1.z12) or (t2.z13=t1.z13) or (t2.z14=t1.z14) or (t2.z15=t1.z15) or
		 (t2.z16=t1.z16) or (t2.z17=t1.z17) or (t2.z18=t1.z18) or (t2.z19=t1.z19) or (t2.z20=t1.z20)  ) 
	 ) as T
	 where T.id >502
		 