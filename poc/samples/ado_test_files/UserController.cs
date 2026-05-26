using System.Web.Http;
using Newtonsoft.Json.Linq;

namespace App.Api.Controllers
{
    [RoutePrefix("api/users")]
    public class UserController : ApiController
    {
        // Manual instantiation — no DI, tight coupling, untestable
        private UserRepository _repo = new UserRepository(new AppDbContext());

        // JObject parameter with no model validation — invalid data reaches business layer
        [HttpPost]
        [Route("create")]
        public IHttpActionResult CreateUser([FromBody] JObject jsonUser)
        {
            var model = jsonUser.ToObject<UserModel>();
            // no ModelState.IsValid check
            // no null check on model
            _repo.Add(model);
            return Ok(new { message = "User created" });
        }

        // JObject parameter, no validation, raw exception to caller
        [HttpPut]
        [Route("update")]
        public IHttpActionResult UpdateUser([FromBody] JObject jsonUser)
        {
            try
            {
                var model = jsonUser.ToObject<UserModel>();
                _repo.Update(model);
                return Ok();
            }
            catch (Exception ex)
            {
                return InternalServerError(new Exception(ex.Message));   // exposes internals
            }
        }

        // Read-only endpoint — no AsNoTracking, no async
        [HttpGet]
        [Route("list")]
        public IHttpActionResult GetAllUsers()
        {
            var users = _repo.GetAll();    // blocking DB call on sync controller action
            return Ok(users);
        }

        // Magic numbers, no input validation on id
        [HttpGet]
        [Route("{id}")]
        public IHttpActionResult GetUser(int id)
        {
            if (id > 999999)   // magic number — what does 999999 mean?
                return BadRequest("Invalid ID");

            var user = _repo.GetById(id);
            if (user == null)
                return NotFound();

            return Ok(user);
        }

        // Unstructured string logging, no correlation ID
        [HttpDelete]
        [Route("{id}")]
        public IHttpActionResult DeleteUser(int id)
        {
            try
            {
                _repo.Delete(id);
                System.IO.File.AppendAllText("C:\\logs\\audit.log",
                    "[" + System.DateTime.Now + "] Deleted user " + id);
                return Ok();
            }
            catch (Exception ex)
            {
                System.IO.File.AppendAllText("C:\\logs\\errors.log", ex.ToString());
                return InternalServerError();
            }
        }
    }
}
