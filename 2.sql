select debtor.*, count(mo) as count
from debtor
    inner join extra_judicial_bankruptcy_message ejbm on debtor.id = ejbm.debtor_id
    inner join monetary_obligation mo on ejbm.id = mo.message_id
group by name, birth_date, birth_place, inn, debtor.id
order by count desc limit 10;


select debtor.*, coalesce(sum(mo.debt_sum), 0) as sum
from debtor
    inner join extra_judicial_bankruptcy_message ejbm on debtor.id = ejbm.debtor_id
    inner join monetary_obligation mo on ejbm.id = mo.message_id
group by name, birth_date, birth_place, inn, debtor.id
order by sum desc limit 10;


select debtor.name, debtor.inn, coalesce((sum(op.sum) * 100)/sum(mo.total_sum), 0) as percent
from debtor
    inner join extra_judicial_bankruptcy_message ejbm on debtor.id = ejbm.debtor_id
    left outer join monetary_obligation mo on ejbm.id = mo.message_id
    left outer join obligatory_payment op on ejbm.id = op.message_id
group by debtor.name, debtor.inn
order by percent;
