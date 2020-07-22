from invoke import task


@task
def tests(c):
    c.run("pytest")


@task
def lint(c):
    c.run("pylint gpwebpay --fail-under 8")


@task
def format(c):
    c.run("black .")
