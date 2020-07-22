from invoke import task


@task
def tests(c):
    c.run("pytest")


@task
def lint(c):
    c.run("pylint gpwebpay")


@task
def format(c):
    c.run("black .")
